from celery import shared_task
from .utils import assignment_report
from canvasapi import Canvas
from .models import ReportRequest
import pandas as pd
from django.core.files import File

@shared_task
def add(x, y):
    return x + y

@shared_task
def generate_report(CANVAS_URL, CANVAS_TOKEN, report_request_id, course_id, assignment_id):
    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
    print("Getting submissions")
    submissions = assignment_report.get_submissions(canvas, course_id, assignment_id)
    print("Getting rubric")
    rubric = assignment_report.get_rubric(canvas, course_id, assignment_id)
    print("Getting headers")
    header_list = assignment_report.get_headers(rubric)
    print("Building report")
    report = assignment_report.build_report(
        canvas, course_id, assignment_id, header_list, submissions, rubric
    )

    # Save report to file and update report_request
    report_request = ReportRequest.objects.get(pk=report_request_id)
    report_request.completed = True

    # Save report to file
    file_name = f"report_{report_request_id}.xlsx"
    report.to_excel(file_name, index=False)

    print(report.head())

    with open(file_name, "rb") as f:
        report_request.file.save(file_name, File(f), save=True)
    

    return True

