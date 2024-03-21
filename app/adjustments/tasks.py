import io
from celery import shared_task
from .utils import adjustment_report
from canvasapi import Canvas
from .models import AdjustmentRequest, AdjustmentProfile
import pandas as pd
from django.core.files import File
from django.core.files.base import ContentFile
import msoffcrypto
from .utils import adjustment_report

import datetime


@shared_task
def generate_report(CANVAS_URL, CANVAS_TOKEN, report_request_id, encryption_password=None, from_date=None):
    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
   
        
    # convert from_date datetime.date to datetime.datetime
    if from_date:
        from_date = datetime.datetime.combine(from_date, datetime.datetime.min.time())


    # Save report to file and update report_request
    report_request = AdjustmentRequest.objects.get(pk=report_request_id)

    # read file into pandas dataframe
    df = pd.read_excel(report_request.file)

    report_request.completed = True

    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)

    course_set_ids = adjustment_report.get_course_set(canvas, dt=from_date)

    students = adjustment_report.get_enrollments(CANVAS_URL, canvas, course_set_ids)

    # Start working on report


    adjustments = adjustment_report.get_adjustment_factors(df, dt=from_date)

    report = adjustment_report.tie_adjustments_to_students(adjustments, students)

    # Save report to file
    
    # Use datetime to create timestamp
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

    file_name = f"{timestamp}_adjustment_report.xlsx"
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        report.to_excel(writer, index=False)

    # Seek to the beginning of the StreamIO object to ensure we read from the start
    output.seek(0)

    # Encrypt the Excel file
    if encryption_password:
        password = encryption_password
        encrypted_output = io.BytesIO()
        file = msoffcrypto.OfficeFile(output)
        file.load_key(password=password)

        # Encrypt the file with the specified password
        file.encrypt(ofile=encrypted_output, password=password)

        # Since encrypt() writes to the encrypted_output, we need to seek to the beginning
        # of this BytesIO object to read its content
        encrypted_output.seek(0)

        # Create a ContentFile from the encrypted BytesIO object
        encrypted_file = ContentFile(encrypted_output.getvalue(), file_name)

        # Save the encrypted file to your Django model
        report_request.file.save(file_name, encrypted_file)
        report_request.completed = True
        report_request.save()
    else:
        report_request.file.save(file_name, File(output, file_name))
        report_request.completed = True
        report_request.save()
    return True


