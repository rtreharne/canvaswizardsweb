from canvasapi import Canvas
import getpass
import datetime
import csv
import pandas as pd
import re
import pickle
import requests
import statistics

# if "config.py" exists, import the variables from it
try:
    from config import CANVAS_URL, CANVAS_TOKEN
except ImportError:
    pass

def get_summary_stats(submissions):
    scores = [x.score for x in submissions if x.score is not None]

    try:
        summary_stats = {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "stdev": statistics.stdev(scores),
            "max": max(scores),
            "min": min(scores),
            "mode": statistics.mode(scores),
        }
    except:
        summary_stats = {
            "mean": None,
            "median": None,
            "stdev": None,
            "max": None,
            "min": None,
            "mode": None,
        }

    return summary_stats

def get_course_set(canvas, dt=None):
    
    admin_courses = []

    try:
        accounts = [x for x in canvas.get_accounts()]
        print("Getting admin courses")
        admin_courses = [x for x in accounts[0].get_courses() if dt < datetime.datetime.strptime(x.created_at, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(weeks=60)]
    except:
        pass

    # my courses
    print("Getting my courses")
    my_courses = [x for x in canvas.get_courses() if dt < datetime.datetime.strptime(x.created_at, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(weeks=60)]

    # create set of admin_courses and my_courses
    course_set = admin_courses + my_courses

    # make sure all objects in the set have uniquie id
    course_dict = {obj.id: obj for obj in course_set}
    course_set = list(course_dict.values())

    return course_set

def get_assignments(course, start, finish):
    
    assignments = [x for x in course.get_assignments() if x.due_at and start < datetime.datetime.strptime(x.due_at, '%Y-%m-%dT%H:%M:%SZ') < finish and x.has_submitted_submissions and x.published]

    return assignments

def get_submission_summary(API_URL, API_TOKEN, course_id, assignment_id):
    url = API_URL + "/api/v1/courses/{}/assignments/{}/submission_summary".format(course_id, assignment_id)
    print(url)

    headers = {'Authorization': 'Bearer ' + API_TOKEN}

    r = requests.get(url, headers= headers)
    return r.json()

def generate_report(CANVAS_URL, CANVAS_TOKEN, start, finish):

    # what years is it?
    current_year = datetime.datetime.now().year

    # create datetime object for 1 Oct.
    dt = datetime.datetime(current_year, 10, 1)

    if dt > datetime.datetime.now():
        dt = datetime.datetime(current_year - 1, 10, 1)

    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)

    courses = get_course_set(canvas, dt=dt)

    # Sort courses by "created_at"
    courses = sorted(courses, key=lambda x: datetime.datetime.strptime(x.created_at, '%Y-%m-%dT%H:%M:%SZ'))
    courses = sorted(courses, key=lambda x: datetime.datetime.strptime(x.created_at, '%Y-%m-%dT%H:%M:%SZ'))

    rows = []

    for course in courses:
        print(course.name)
        assignments = get_assignments(course, start, finish)
        for assignment in assignments:
            row = get_assignment_info(CANVAS_URL, CANVAS_TOKEN, assignment, course)
            rows.append(row)

    df = pd.DataFrame(rows)

    return df

def get_assignment_info(CANVAS_URL, CANVAS_TOKEN, assignment, course):
    submissions = [x for x in assignment.get_submissions()]

    posted_at_dates = [x.posted_at for x in submissions]
    posted_date = max(set(posted_at_dates), key=posted_at_dates.count)

    try:
        posted_date = datetime.datetime.strptime(posted_date, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
    except:
        posted_date = ""

    summary = get_submission_summary(CANVAS_URL, CANVAS_TOKEN, course.id, assignment.id)
    summary_stats = get_summary_stats(submissions)

    row = {
        "course_id": course.id,
        "course_name": course.course_code,
        "assignment_id": assignment.id,
        "assignment_name": assignment.name,
        "due_at": datetime.datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
        "posted_at": posted_date,
        "anonymous_grading": assignment.anonymous_grading,
        "published": assignment.published,
        "points": assignment.points_possible,
        "url": f"{CANVAS_URL}/courses/{course.id}/assignments/{assignment.id}"
    }

    row = {**row, **summary, **summary_stats}

    return row


if __name__ == "__main__":

    print("Starting script ...")

    print("")

    

    start = datetime.datetime(2023, 10, 1)
    finish = datetime.datetime(2023, 12, 1)

    df = generate_report(CANVAS_URL, CANVAS_TOKEN, start, finish)

