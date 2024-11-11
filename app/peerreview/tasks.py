import io
from celery import shared_task
from .utils import assignment_report
from canvasapi import Canvas
from .models import ReportRequest
import pandas as pd
from django.core.files import File
from django.core.files.base import ContentFile
import msoffcrypto

import datetime

@shared_task
def generate_report(CANVAS_URL, CANVAS_TOKEN, report_request_id, course_id, assignment_id, encryption_password=None):
    report = assignment_report.build_report(
        CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id)

    # Save report to file and update report_request
    report_request = ReportRequest.objects.get(pk=report_request_id)
    report_request.completed = True

    # Save report to file
    
    # Use datetime to create timestamp
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

    file_name = f"assignment_report_{course_id}_{assignment_id}_{timestamp}.xlsx"
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
    else:
        report_request.file.save(file_name, File(output, file_name))

    return True


