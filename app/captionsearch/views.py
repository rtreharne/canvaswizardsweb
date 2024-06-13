from django.shortcuts import render
from .forms import CaptionSearchRequestForm, SearchForm
from django.db import IntegrityError
from canvasapi import Canvas
from .models import Course, Caption, Video
from django.utils.datetime_safe import datetime
from .tasks import add_captions
from django.db.models import Q
import re
from functools import reduce
from operator import or_, and_
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.http import HttpResponse
from datetime import datetime as dt
from datetime import timedelta
from django.db.models import Count

def calculate_upload_time(nrows, time_per_row=0.5):
    total_seconds = nrows * time_per_row
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)} hours and {int(minutes)} minutes"

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

            decoded_file = pd.read_csv(file, sep='\t', encoding='utf-8')

            # drop na on transcript_text column
            decoded_file = decoded_file.dropna(subset=["transcript_text"])

            nrows = len(decoded_file)

            # If each row will take 0.5 seconds to upload, calculate how long in sec
            # it will take to do nrows. 
            # Create a string in the format "h hours and m minutes"
            upload_time = calculate_upload_time(nrows)

            iframe = f"<p><iframe style='overflow: auto;' src='https://www.canvaswizards.org.uk/captionsearch/{course.name}?from_iframe=true' width='100%' height='900px'></iframe></p>"

            decoded_file = decoded_file.to_dict(orient='records')
            
            #decoded_file = file.read().decode("utf-8").splitlines()

            add_captions.delay(course.id, decoded_file)

            context['success'] = True
            context['upload_time'] = upload_time
            context['iframe'] = iframe

            return render(request, 'captionsearch/index.html', context)

        else:
            context["form"] = form

            # print form errors
            print("Form errors:")
            print(form.errors)
            return render(request, 'captionsearch/index.html', context)


    context["form"] = CaptionSearchRequestForm()
    return render(request, 'captionsearch/index.html', context)


@csrf_exempt
def course(request, course_name):

    # Check if the request is from an iframe
    #from_iframe = request.GET.get('from_iframe')
    #if not from_iframe:
        #return HttpResponseForbidden("This view can only be accessed from an iframe")
    
    # Get the IP address of the client
    ip = request.META.get('REMOTE_ADDR')

    # Get the current time
    now = datetime.now()

    # Get the list of timestamps for this IP
    timestamps = cache.get(ip, [])

    # Remove timestamps older than 1 minute
    one_minute_ago = now - timedelta(minutes=1)
    timestamps = [timestamp for timestamp in timestamps if timestamp > one_minute_ago]

    # Check if the rate limit has been exceeded
    if len(timestamps) >= 5:  # Limit to 10 requests per minute
        return HttpResponse('Too many requests', status=429)

    course = Course.objects.get(name=course_name)
    videos = Video.objects.select_related('course').filter(course=course).order_by('-date', '-time')
    context = {
        "course": course,
        "videos": videos,
    }

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            words = query.split(" AND " if " AND " in query else " ")
            q_objects = [Q(transcript_text__icontains=word) | Q(owner__icontains=word) for word in words]
            operator = and_ if " AND " in query else or_
            captions = Caption.objects.filter(reduce(operator, q_objects), video__course=course)

            # Count unique videos and order by count
            video_counts = (captions.values('video__title')  # Group by video title
                            .annotate(count=Count('video'))  # Count distinct videos
                            .order_by('-count'))  # Order by count descending

            # Convert to list of tuples
            # # Convert to list of dictionaries
            video_counts = [{"title": item['video__title'], "count": item['count']} for item in video_counts]            
            context["captions"] = captions
            context["query"] = query
            context["video_counts"] = video_counts[:10]
            context["form"] = SearchForm()
        else:
            print("form invalid")
            context["form"] = form

        return render(request, 'captionsearch/course.html', context)

    form = SearchForm()
    context["form"] = form

    return render(request, 'captionsearch/course.html', context)