import io
from celery import shared_task

from .models import Video, Caption, Course
from django.utils.datetime_safe import datetime

@shared_task
def add_caption(course_id, line):

    course = Course.objects.get(id=course_id)

    fields = line.split("\t")

    if fields[5] != "":
        fields = line.split("\t")
        video_url = fields[0]
        date = datetime.strptime(fields[1], "%m/%d/%Y").date()
        time = datetime.strptime(fields[2], "%I:%M %p").time()
        transcript_url = fields[3]
        transcript_text = fields[4]
        transcript_timestamp = fields[5]
        title = fields[6]
        owner = fields[7]

        # Create video object if it doesn't exist
        try:
            video = Video.objects.get(video_url=video_url)
        except:
            video = Video(
                video_url = video_url,
                title = title,
                course = course,
                date = date,
                time = time
            )
            video.save()

        # Check if caption object exists
        try:
            check = Caption.objects.get(video=video, transcript_text=transcript_text)
            print("Caption object already exists!")
        except:

            # Create caption object
            caption = Caption(
                video=video,
                transcript_url=transcript_url,
                transcript_text = transcript_text,
                transcript_timestamp = transcript_timestamp,
                title = title,
                owner = owner
            )


            caption.save()
    
    return "Caption Added"

@shared_task
def add_captions(course_id, decoded_file):

    # Let's create the captions
    for line in decoded_file:
        add_caption.delay(course_id, line)
    
    return "Done"


    

