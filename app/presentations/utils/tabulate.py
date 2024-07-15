from canvasapi import Canvas
import pandas as pd
from ..models import PresentationRequest

# from django settings import ACCOUNT_DEFAULT_HTTP_PROTOCOL
from django.conf import settings
ACCOUNT_DEFAULT_HTTP_PROTOCOL = getattr(settings, 'ACCOUNT_DEFAULT_HTTP_PROTOCOL')

def get_module_by_name(modules, name):
    for module in modules:
        if module.name == name:
            return module
    return None

def get_page_by_title(pages, title):
    for page in pages:
        if page.title == title:
            return page
    return None

def create(CANVAS_URL, CANVAS_TOKEN, course_id, assignment_id):
    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    submissions = assignment.get_submissions(include=["user"])
    group_set_labels = [x.name for x in course.get_group_categories()]
    group_sets = [[y for y in x.get_groups()] for x in course.get_group_categories()]

    data = []

    for label, set in zip(group_set_labels, group_sets):
        for s in set:
            members = [x.user_id for x in s.get_memberships()]
            for sub in submissions:
                try:
                    if sub.user['id'] in members:
                        data.append({
                            'Name': sub.user['sortable_name'],
                            'set': label,
                            'group': s,
                            'File': sub.attachments[0].url,
                            'Marker': f"{CANVAS_URL}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={sub.user['id']}"
                        })
                except:
                    continue

    for sub in submissions:
        try:
            
            data.append({
                'Name': sub.user['sortable_name'],
                'set': 'All Students',
                'group': 'All Students',
                'File': sub.attachments[0].url,
                'Marker': f"{CANVAS_URL}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={sub.user['id']}"
            })
        except:
            continue

    df = pd.DataFrame(data)
    df = df.sort_values(by=['Name'])
    html = df.to_html(index=False, escape=False)

    return html

def create_module(CANVAS_URL, CANVAS_TOKEN, course_id, report_request_id, domain):
    print("creating/updating module")
    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
    course = canvas.get_course(course_id)

    presentation_request = PresentationRequest.objects.get(pk=report_request_id)

    # create a canvas module called Canvas Wizards Showcase Incantation
    modules = [x for x in course.get_modules()]

    module = get_module_by_name(modules, 'Canvas Wizards Showcase Incantation')

    if not module:
        module = course.create_module({'name': 'Canvas Wizards Showcase Incantation'})

    pages = [x for x in course.get_pages()]

    page = get_page_by_title(pages, presentation_request.assignment_name)

    #print("<iframe src='{0}://{1}/showcase/{2}' width='100%' height='800' frameborder='0' sandbox='allow-scripts allow-same-origin'></iframe>".format(ACCOUNT_DEFAULT_HTTP_PROTOCOL,domain, presentation_request.uuid))


    if not page:
        new_page = course.create_page(
            wiki_page={
                "title": presentation_request.assignment_name,
                "body": "<iframe src='{0}://{1}/showcase/{2}' width='100%' height='800' frameborder='0' sandbox='allow-scripts allow-same-origin allow-forms allow-popups allow-downloads'></iframe>".format(ACCOUNT_DEFAULT_HTTP_PROTOCOL,domain, presentation_request.uuid)
            }
        )
    else:
        page.edit(
            wiki_page={
                "title": presentation_request.assignment_name,
                "body": "<iframe src='{0}://{1}/showcase/{2}' width='100%' height='800' frameborder='0' sandbox='allow-scripts allow-same-origin allow-forms allow-popups allow-downloads'></iframe>".format(ACCOUNT_DEFAULT_HTTP_PROTOCOL,domain, presentation_request.uuid)
            }
        )

    # add new_page to new_module
    module.create_module_item(
        module_item={
            "type": "Page",
            "content_id": page.page_id,
            "page_url": page.url,
            "title": page.title
        }
    )

    return "Item created/updated."