from django.shortcuts import render
from .forms import EnrollmentsForm
import pandas as pd
from canvasapi import Canvas
import requests

def user_search(account_id, user, API_TOKEN):
    url = f"https://canvas.liverpool.ac.uk/api/v1/accounts/{account_id}/users"
    params = {
        "search_term": user
    }
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    response = requests.get(url, params=params, headers=headers)
    return response

def account_user(canvas, user, API_TOKEN):
    accounts = [x for x in canvas.get_accounts()]

    for a in accounts:
        response = user_search(a.id, user, API_TOKEN)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
        
def get_enrollments_by_user_id(course, user_id, enrollment_type="TeacherEnrollment"):
    enrollments = [x for x in course.get_enrollments(user_id=user_id) if x.type == enrollment_type]
    if len(enrollments) > 0:
        return enrollments[0]

def enrollments(request):

    context = {}

    if request.method == 'POST':
        form = EnrollmentsForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            canvas_url = form.cleaned_data['canvas_url']
            canvas_token = form.cleaned_data['canvas_token']
            action = form.cleaned_data['action']
            notify = bool(form.cleaned_data['notify'])

            if notify:
                enrollment_state = "invited"
            else:
                enrollment_state = "active"

            canvas = Canvas(canvas_url, canvas_token)

            df = pd.read_excel(file)

            status = []
            detail = []

            for i, row in df.iterrows():

                print(row)

                if row['enrollment_type'] not in ["TeacherEnrollment", "StudentEnrollment"]:
                    status.append("Error")
                    detail.append("Invalid enrollment type.")
                    continue

                try:
                    course = canvas.get_course(row["course_code"], use_sis_id=True)
                except:
                    status.append("Error")
                    detail.append("You do not have access to this course.")
                    continue
                
                try:
                    user = account_user(canvas, row["email"], canvas_token)[0]
                except:
                    status.append("Error")
                    detail.append("Couldn't find user.")
                    continue
                
                if action == "add":
                    new_enrollment = course.enroll_user(user=user['id'], enrollment_type=row["enrollment_type"], enrollment={
                    "enrollment_state": enrollment_state
                    })
                    status.append("Success")
                    detail.append("User enrollment created.")
                elif action == "delete":
                    enrollment = get_enrollments_by_user_id(course, user['id'], row["enrollment_type"])
                    if enrollment:
                        enrollment.deactivate(task="delete")
                        status.append("Success")
                        detail.append("User enrollment deleted.")
                    else:
                        status.append("Error")
                        detail.append("User enrollment not found.")
                elif action == "conclude":
                    enrollment = get_enrollments_by_user_id(course, user['id'], row["enrollment_type"])
                    if enrollment:
                        enrollment.deactivate(task="conclude")
                        status.append("Success")
                        detail.append("User enrollment concluded.")
                    else:
                        status.append("Error")
                        detail.append("User enrollment not found.")

            df["status"] = status
            df["detail"] = detail

            log = df.to_dict(orient="records")

            context["log"] = log

            form = EnrollmentsForm()
            context["form"] = form

            pass
    else:
        form = EnrollmentsForm()
        context["form"] = form
        

    return render(request, 'tools/enrollments.html', context)
