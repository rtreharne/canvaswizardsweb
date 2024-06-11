from django.shortcuts import render
from .forms import CaptionSearchRequestForm, SearchForm
from django.db import IntegrityError
from canvasapi import Canvas
from .models import Course, Caption, Video
from django.utils.datetime_safe import datetime
from .tasks import add_captions
from django.db.models import Q
import re

def index(request):
    context = {}

    if request.method == 'POST':
        form = CaptionSearchRequestForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the form
            context["form"] = CaptionSearchRequestForm()
            context["message"] = "Form submitted successfully."

            canvas_token = form.cleaned_data["canvas_token"]
            canvas_url = form.cleaned_data["canvas_url"]
            course_id = form.cleaned_data["course_id"]
            file = form.cleaned_data["file"]

            canvas = Canvas(canvas_url, canvas_token)
            try:
                course = canvas.get_course(course_id)
            except:
                context["error"] = "Canvas token not authorised to access course."
                return render(request, 'captionsearch/index.html', context)

            course_name = course.course_code

            # strip trailing / from canvas_url
            if canvas_url[-1] == "/":
                canvas_url = canvas_url[:-1]

            course_url = f"{canvas_url}/courses/{course_id}"

            # Create course object if it doesn't exist
            try:
                course, created = Course.objects.get_or_create(name=course_name, url=course_url)
            except IntegrityError:
                course = Course.objects.get(name=course_name)

            
            # Let's read the .tsv file

            # Determine encoding first
            
            decoded_file = file.read().decode("ISO-8859-1").splitlines()

            # Let's check if the headers are correct
            headers = decoded_file[0].split("\t")

            add_captions.delay(course.id, decoded_file)

            context['message'] = f"Fantastic! I'm making your captions searchable now. You can search your captions at the following URL.<br><br><a href='{course.name}'>https://www.canvaswizards.org.uk/captionsearch/{course.name}</a><br><br>Be sure to share the link with your students."

            return render(request, 'captionsearch/index.html', context)

        else:
            context["form"] = form

            # print form errors
            print("Form errors:")
            print(form.errors)
            return render(request, 'captionsearch/index.html', context)


    context["form"] = CaptionSearchRequestForm()
    return render(request, 'captionsearch/index.html', context)

def course(request, course_name):

    course = Course.objects.get(name=course_name)
    videos = Video.objects.filter(course=course).order_by('-date', '-time')
    context = {
        "course": course,
        "videos": videos,
    }

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            if " AND " in query:
                words = query.split(" AND ")
                q_objects = Q()
                for word in words:
                    q_objects &= Q(transcript_text__icontains=word)
            else:
                words = query.split()
                q_objects = Q()
                for word in words:
                    q_objects |= Q(transcript_text__icontains=word)

            captions = Caption.objects.filter(q_objects, video__course=course)

            for caption in captions:
                caption.transcript_text = re.sub(f'({query})', r'<span class="highlight">\1</span>', caption.transcript_text, flags=re.IGNORECASE)

            context["captions"] = captions
            context["query"] = query
            context["form"] = SearchForm()
        else:
            print("form invalid")
            context["form"] = form

        return render(request, 'captionsearch/course.html', context)
        

    form = SearchForm()
    context["form"] = form

    return render(request, 'captionsearch/course.html', context)
