from celery import shared_task
from .utils import tabulate
from .models import PresentationRequest
@shared_task
def task_showcase(CANVAS_URL, CANVAS_TOKEN, report_request_id, course_id, assignment_id, domain):
    html = tabulate.create(CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id)
    report_request = PresentationRequest.objects.get(pk=report_request_id)
    report_request.completed = True
    report_request.html = html
    report_request.save()

    module = tabulate.create_module(CANVAS_URL, CANVAS_TOKEN, course_id, report_request.id, domain)

    print(module)

    return "done!"
