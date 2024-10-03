from canvasapi import Canvas
import getpass
import datetime
import csv
import pandas as pd
import re
import pickle

# if "config.py" exists, import the variables from it
try:
    from config import CANVAS_URL, CANVAS_TOKEN
except ImportError:
    pass

def get_course_set(canvas, dt=None):

    print(dt)
    
    # Get my accounts
    print("Getting accounts ...")
    accounts = [x for x in canvas.get_accounts()]

    print("")

    print("Getting courses ...")
    courses = [x for x in accounts[0].get_courses() if dt < datetime.datetime.strptime(x.created_at, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(weeks=60)]

    courses_with_quizzes = []
    for course in courses:
        ass = [x.course_id for x in course.get_assignments() if x.due_at and dt < datetime.datetime.strptime(x.due_at, '%Y-%m-%dT%H:%M:%SZ') and "external_tool" in x.submission_types]
        courses_with_quizzes.extend(ass)

    return list(set(courses_with_quizzes))

def add_student(CANVAS_URL, enrollment, students, course):
    student_id = get_student_id_from_sis_user_id(enrollment.sis_user_id)
    course_info = {
        "course": course.course_code,
        "url": f"{CANVAS_URL}/courses/{course.id}/assignments"
    }

    print(student_id, student_id in students)

    if student_id in students:

        students[student_id].append(course_info)

    else:
        students[student_id] = [course_info]

    return students

def get_enrollments(CANVAS_URL, canvas, course_set_ids):

    students = {}

    for course_id in course_set_ids:
        course = canvas.get_course(course_id)
        enrollments = [x for x in course.get_enrollments() if x.type=="StudentEnrollment"]
        for enrollment in enrollments:
            student_id = get_student_id_from_sis_user_id(enrollment.sis_user_id)
            info = [{
                "course": course.course_code,
                "url": f"{CANVAS_URL}/courses/{course.id}/assignments"
            }]
            if student_id in students:
                students[student_id].extend(info)
            else:
                students[student_id] = info

    return students

def get_adjustment_factors(df, dt=None):
    
    # Drop duplicates
    df = df.drop_duplicates(['Spider ID','Exam Adjustments (Listed Separately)'])

    # Convert Adjusted Date to datetime
    df["Adjustment Date"] = pd.to_datetime(df["Adjustment Date"], errors="coerce")


    students = list(set(df["Spider ID"].tolist()))

    rows = []
    for student in students:


        factor = 1
        factors = []
        subset = df[df["Spider ID"] == student]
        row_dict = {"Student ID": student}

        # Get most recent Adjusted At date for student
        dates = subset["Adjustment Date"].tolist()
        if len(dates) != 0:
            row_dict["Adjustment Date"] = max(dates).date()
        else:
            row_dict["Adjustment Date"] = None

        
        
        for i, row in subset.iterrows():
            
            num = re.findall(r'\d+', row["Exam Adjustments (Listed Separately)"])
            if len(num) != 0:
                factors.extend(num)
            
        if len(factors) != 0:
            
            factor += float(list(set(factors))[0])/100

        for i, row in subset.iterrows():
            if "toilet breaks" in row["Exam Adjustments (Listed Separately)"].lower():
                factor += 0.083
            if "rest breaks" in row["Exam Adjustments (Listed Separately)"].lower():
                factor += 0.25

            row_dict["Surname"] = row["Surname"]
            row_dict["First Name"] = row["First Name"]
    
            
        row_dict["Adjustment Factor"] = factor
        rows.append(row_dict)

    
    df2 = pd.DataFrame(rows)
    df2 = df2.dropna()

    return df2

def get_student_id_from_sis_user_id(sis_user_id):
        return re.findall(r'\d+', sis_user_id)[0]

def tie_adjustments_to_students(adjustments, students):

    rows = []

    for i, s in adjustments.iterrows():
        try:
            data = students[str(s["Student ID"])]
            for d in data:
                row = {
                    "student_id": s["Student ID"],
                    "surname": s["Surname"],
                    "first_name": s["First Name"],
                    "adjustment_date": s["Adjustment Date"],
                    "adjustment_factor": s["Adjustment Factor"],
                    "course": d["course"],
                    "url": d["url"]
                }
                rows.append(row)
        except:
            continue

    report = pd.DataFrame(rows)

    # format report "adjustment_date" column to datetime
    report["adjustment_date"] = pd.to_datetime(report["adjustment_date"], errors="coerce")

    # Then convert column to string format '%YYYY-%mm-%dd'
    report["adjustment_date"] = report["adjustment_date"].dt.strftime('%Y/%m/%d')

    return report


if __name__ == "__main__":

    print("Starting script ...")

    print("")

    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)

    #course_set_ids = get_course_set(canvas)

    course_set_ids = [67269, 67499]

    print("Getting enrollments ...")

    students = get_enrollments(CANVAS_URL, canvas, course_set_ids)

    #pickle students
    with open("students.pickle", "wb") as f:
        pickle.dump(students, f)

    # Start working on report

    df = pd.read_excel("adjustments.xlsx")

    adjustments = get_adjustment_factors(df, dt=None)

    report = tie_adjustments_to_students(adjustments, students)

