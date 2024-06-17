from django.shortcuts import render
from .forms import EnrollmentsForm
import pandas as pd
from canvasapi import Canvas

def enrollments(request):

    context = {}

    if request.method == 'POST':
        form = EnrollmentsForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            canvas_url = form.cleaned_data['canvas_url']
            canvas_token = form.cleaned_data['canvas_token']
            action = form.cleaned_data['action']
            notify = form.cleaned_data['notify']

            canvas = Canvas(canvas_url, canvas_token)

            df = pd.read_excel(file)

            status = []
            detail = []

            for i, row in df.iterrows():

                try:
                    course = canvas.get_course(row["course_code"], use_sis_id=True)
                except:
                    status.append("Error")
                    detail.append("You do not have access to this course.")
                    continue
                
                
                course.enroll_user(user=row["user_id"], enrollment={
                    "enrollment_type": row["enrollment_type"],
                    "active": not notify
                })

                status.append("Success")
                if action == "add":
                    detail.append("User enrollment created.")
                else:
                    detail.append("User enrollment deleted.")

            df["status"] = status
            df["detail"] = detail

            log = df.to_dict(orient="records")

            context["log"] = log

            print(df)

            form = EnrollmentsForm()
            context["form"] = form

            pass
    else:
        form = EnrollmentsForm()
        context["form"] = form
        

    return render(request, 'tools/enrollments.html', context)
