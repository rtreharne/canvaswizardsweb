from canvasapi import Canvas
import getpass
import datetime
import csv
import pandas as pd
import re
import requests

def main():
    print(
"""
                      ░▓▓░   ░░                             
                       ░░    ▓▓                             
                   ░░       ░██░       ░░                   
                 ░░█▒░  ░██████████░  ░▒█░░                 
            ░▒░  ░░█▒░░     ░██░      ░▒█░░ ░░▒░            
             ▒     ░░        ▓▓        ░░    ░▒             
                    ░░░      ░░      ░░░                    
                 ▓███████▓░      ░▓███████▓                 
        ░▒▒░   ▒██▒░░░  ▒██▒░  ░▒██▒░░▒ ░▒██▒   ░▒▒░        
        ░███▓ ░██░░█▒    ░██░░░░██░░▓▓░▒█░░██░ ▓███░        
        ░▓░▓█▒▒█▒░▓░      ▒██████▒░█░░█░░  ▒█▒▒█▓░▓░        
         ░ ▒█▓░██░        ▓█▒░░▒█▓░░▓▓░   ░██░▓█▓ ░         
          ░▓██░▓█▓░     ░▒██░  ░▓█▓░     ░▓█▓░██▓░          
          ░████░░███▓▓▓███▒░    ░▒███▓▓▓███░░████░          
          ▒▒▒██░  ░▒▓▓▓▒░░        ░░▒▓▓▓▒░  ░██▒▒▒          
           ░███░       ░░░░      ░░░░       ░███░           
           ▒███░     ▒██████▒  ▒██████▒     ░███▒           
          ░██▒░    ▒████████████████████▒    ░▒██░          
         ░▓█████▓███████████▒░░▒███████████▓▓████▓░         
         ░███████████████▓░      ░▒███████████████░         
         ▓██▓███░░░░░░░     ░▓▓░     ░░░░░░░███▓██▓░        
        ░▓█░▓█████▓▓▓▓▓ ░  ▒████▒  ░ ▓▓▓▓▓█████▓░█▓░        
         ▒▓░███████████░▓░░██████░░█░███████████░▓▒         
          ░ █████████████▓▒██████▒▓█████████████ ░          
            ░██▒████████████████████████████▒██░            
             ▓█░████████████████████████████░█▓░            
             ░▓░▒██████████████████████████▒░▓░             
                 ▓██▒▓████████████████▓▒██▓                 
                 ░██▒░███▓▓███████▓███▒▒██░                 
                   ▒█░▒██▓▒██████▓▒██▒░█▒                   
                    ░░░░██░▓█████░▓█░ ░░                    
                         ▒▒░▓███░▒▒░                        
                             ▒▓                                             
""" )
    print("")
    print("www.canvaswizards.org.uk")
    print("")
    print("Welcome to the Canvas Assignment Report Generator!")
    print("By Robert Treharne, University of Liverpool. 2024")
    print("")

    # if config.py exists, import it
    try:
        from config import CANVAS_URL, CANVAS_TOKEN
    except ImportError:
        CANVAS_URL = input('Enter your Canvas URL: ')
        print("")
        CANVAS_TOKEN = getpass.getpass('Enter your Canvas token: ')
        print("")

    # if course_id in config.py, use it
    try:
        from config import course_id
    except ImportError:
        course_id = int(input('Enter the course ID: '))
        print("")

    # if assignment_id in config.py, use it
    try:
        from config import assignment_id
    except ImportError:
        assignment_id = int(input('Enter the assignment ID: '))
        print("")

    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)

    print("Getting submissions...")
    submissions = get_submissions(canvas, course_id, assignment_id)
    print("Getting rubric...")
    rubric = get_rubric(canvas, course_id, assignment_id)
    print("Building headers...")
    header_list = get_headers(rubric)
    print("Building report...")
    build_report(canvas, course_id, assignment_id, header_list, submissions, rubric)

def get_submissions(canvas, course_id, assignment_id):
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    submissions = [x for x in assignment.get_submissions(include=["user", "submission_comments", "rubric_assessment"])]
    return submissions

def get_rubric(canvas, course_id, assignment_id):
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    try:
        return assignment.rubric
    except:
        return None

def get_headers(rubric):

    if rubric:
        rubric_rating_headers = [f"RATING_{x['description']}" for x in rubric]
        rubric_score_headers = [f"SCORE_{x['description']}" for x in rubric]

    header_list = [
        "last_name",
        "first_name",
        "sis_user_id",
        "anonymous_id",
        "url",
        "submitted_at",
        "seconds_late",
        "status",
        "posted_at",
        "score",
        "grader",
        "comments",
        "student_viewed_feedback",]

    if rubric:
        header_list += rubric_rating_headers + rubric_score_headers

    return header_list

def get_rubric_rating(rubric, rubric_assessment):
    """
    Retrieves the descriptions of the ratings for each rubric item in the rubric assessment.

    Parameters:
    rubric (list): A list of rubric items.
    rubric_assessment (dict): A dictionary containing the rubric assessment data.

    Returns:
    list: A list of rating descriptions for each rubric item in the rubric assessment.
    """
    ratings_list = []
    rubric_flag = False
    for item in rubric:
        rating_id = rubric_assessment[item["id"]]["rating_id"]
        for ratings in item["ratings"]:
            if ratings["id"] == rating_id:
                if ratings["description"]:
                    ratings_list.append(ratings["description"])
                    rubric_flag = True
                else:
                    ratings_list.append("")
        if rubric_flag:
            rubric_flag = False
        else:
            ratings_list.append("")
            
    return ratings_list

def get_rubric_score(rubric, rubric_assessment):
    """
    Calculates the score for each rubric item based on the rubric assessment.

    Parameters:
    rubric (list): The rubric containing the criteria and ratings.
    rubric_assessment (dict): The rubric assessment containing the rating for each rubric item.

    Returns:
    list: A list of scores for each rubric item.
    """
    ratings_list = []
    for item in rubric:
        rating_id = rubric_assessment[item["id"]]["rating_id"]
        for ratings in item["ratings"]:
            if ratings["id"] == rating_id:
                    ratings_list.append(ratings["points"])
        if rating_id is None:
            try:
                ratings_list.append(rubric_assessment[item["id"]]["points"])
            except:
                ratings_list.append("")   
        
    return ratings_list

def read_annotations(CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id, user_id):
    # Define the base URL
    base_url = f"{CANVAS_URL}/api/v1/courses"

    # Define the headers (replace 'YourToken' with your actual token)
    headers = {
        "Authorization": f"Bearer {CANVAS_TOKEN}"
    }

    # Make the GET request
    response = requests.get(f"{base_url}/{course_id}/assignments/{assignment_id}/submissions/{user_id}/document_annotations/read", headers=headers)

    # Print the response
    return response.json()["read"]

def build_submission_string(CANVAS_URL, CANVAS_TOKEN, canvas, course_id, assignment_id, header_list, rubric, submission, enrollments=None, anonymous_grading=False):
    """
    Builds a row of data for a submission in a Canvas assignment report.

    Args:
        submission (Submission): The submission object representing a student's submission.

    Returns:
        list: A list containing the row of data for the submission, including student information,
              submission details, grading information, and rubric ratings and scores.
    """
    try:
        student_viewed_feedback = read_annotations(CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id, submission.user_id)
    except:
        student_viewed_feedback = ""

    if enrollments:

        try:
            user = get_user_from_id(enrollments, submission.user_id)            
            sortable_name = user["sortable_name"]
            last_name, first_name = user["sortable_name"].split(", ")
            sis_user_id = user["sis_user_id"]
        except:
            anonymous_id = ""
            last_name = ""
            first_name = ""
            sortable_name = ""
            sis_user_id = ""
            url = ""
        try:
            anonymous_id = submission.anonymous_id
            url = f"{CANVAS_URL}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&anonymous_id={anonymous_id}"
        except:
            anonymous_id = ""
            url = ""
            
    else:
        try:
            anonymous_id = submission.anonymous_id
            url = f"{CANVAS_URL}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&anonymous_id={submission.anonymous_id}"
            sortable_name = f'{submission.user["sortable_name"]}'
            last_name, first_name = sortable_name.split(", ")
            sis_user_id = submission.user["sis_user_id"]
        except:
            anonymous_id = ""
            last_name = ""
            first_name = ""
            sortable_name = ""
            sis_user_id = ""
    
    try:
        if not anonymous_grading:
            url = f"{CANVAS_URL}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={submission.user_id}"
        submitted_at = submission.submitted_at
        seconds_late = submission.seconds_late
        status = submission.workflow_state
        posted_at = submission.posted_at
        score = submission.score
    except:
        submitted_at = ""
        seconds_late = ""
        status = ""
        posted_at = ""
        score = ""

    try:
        grader = canvas.get_user(submission.grader_id).sortable_name
    except:
        grader = ""
    
    if rubric:
        try:
            rubric_assessment = submission.rubric_assessment
        except:
            rubric_assessment = ""
        

        if rubric_assessment:
            rubric_rating = get_rubric_rating(rubric, rubric_assessment)
            rubric_score = get_rubric_score(rubric, rubric_assessment)
        else:
            rubric_rating = [""]*len(rubric)
            rubric_score = [""]*len(rubric)

    comments = ", ".join([f"{x['author_name']} - {x['comment']}" for x in submission.submission_comments])


    values = [
        last_name,
        first_name,
        sis_user_id,
        anonymous_id,
        url,
        submitted_at,
        seconds_late,
        status,
        posted_at,
        score,
        grader,
        comments,
        student_viewed_feedback,
    ]

    if rubric:
        values += rubric_rating + rubric_score

    row = {}

    for header, value in zip(header_list, values):
        row[header] = value
        
    return row

def get_user_from_id(enrollments, user_id):
    for enrollment in enrollments:
        if enrollment.user_id == user_id:
            return enrollment.user
    return None

def build_report(CANVAS_URL, CANVAS_TOKEN, canvas, course_id, assignment_id, header_list, submissions, rubric, enrollments=None) -> None:
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{course_id}_{assignment_id}.xlsx"

    assignment = canvas.get_course(course_id).get_assignment(assignment_id)
    print(assignment.anonymous_grading)
    if assignment.anonymous_grading:
        print("Getting enrollments...")
        enrollments = [x for x in canvas.get_course(course_id).get_enrollments(include=["user"])]
    else:
        enrollments = None
        
    data = []
    for submission in submissions:
        row = build_submission_string(CANVAS_URL, CANVAS_TOKEN, canvas, course_id, assignment_id, header_list, rubric, submission, enrollments=enrollments, anonymous_grading=assignment.anonymous_grading)
        if row:
            data.append(row)

    df = pd.DataFrame(data)

    if rubric:
        df['rubric_issue'] = False

        # look at all columns that contain the word 'SCORE' if any values are missing, and if status == 'graded', set rubric_issue to True
        for index, row in df.iterrows():
            if row['status'] == 'graded':
                for header in header_list:
                    if 'SCORE' in header:
                        if not isinstance(row[header], (int, float)):
                            df.at[index, 'rubric_issue'] = True

    try:
        df.sort_values(by='anonymous_id', inplace=True)

        # reset the index, but start at 1
        df.reset_index(drop=True, inplace=True)

        # add 1 to the index
        df.index += 1

        # rename the index to 'student_number'
        df.index.name = 'student'

        # make index first column
        df.reset_index(inplace=True)

        # move 'student' column to first column
        #cols = list(df.columns)
        #cols = [cols[-1]] + cols[:-1]
        #df = df[cols]


    except:
        pass
        
    return df



def sort_key(s):
    match = re.match(r'(\d+)', s)
    if match:
        # For strings starting with digits, the key is the numeric value followed by the string itself
        return (int(match.group(1)), s)
    else:
        # For strings starting with letters, the key is a large number followed by the string itself
        return (float('inf'), s)





if __name__ == "__main__":
    main()