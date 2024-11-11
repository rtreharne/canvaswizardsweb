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
    print("Welcome to the Canvas Peer Review Summary Report Generator!")
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

    print("Building report...")
    report = build_report(CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id)
    print(report)


def get_submissions(canvas, course_id, assignment_id):
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    submissions = [x for x in assignment.get_submissions(include=["user", "submission_comments", "rubric_assessment"])]
    return submissions

def get_submission(submissions, submission_id):
    for submission in submissions:
        if submission.id == submission_id:
            return submission

def get_rubric_assessments(canvas, course_id, assignment_id):
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    rubric_id = assignment.rubric_settings["id"]
    rubric_return = course.get_rubric(rubric_id, include=["peer_assessments"])
    return rubric_return.assessments

def create_user_dict(canvas, course_id):
    course = canvas.get_course(course_id)
    enrollments = [x for x in course.get_enrollments(include=["user"]) if x.type == "StudentEnrollment"]
    user_dict = {x.user["id"]: x.user["sortable_name"] for x in enrollments}
    return user_dict

def build_report(CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id):
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{course_id}_{assignment_id}.xlsx"

    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)

    submissions = get_submissions(canvas, course_id, assignment_id)
    rubric_assessments = get_rubric_assessments(canvas, course_id, assignment_id)
    user_dict = create_user_dict(canvas, course_id)

    rows = []
    for review in rubric_assessments:
        submission = get_submission(submissions, review["artifact_id"])
        if submission:
            row = {
                "student_name": user_dict[submission.user_id],
                "student_id": submission.user["sis_user_id"][:9],
                "assessor_name": user_dict[review["assessor_id"]],
                "score": review["score"],
                "submission_url": f"{CANVAS_URL}courses/{course_id}/assignments/{assignment_id}/submissions/{submission.id}"
            }
            rows.append(row)

    df = pd.DataFrame(rows)
        
    return df


if __name__ == "__main__":
    main()