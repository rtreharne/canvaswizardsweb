import io
from celery import shared_task
import pandas as pd

from .models import Video, Caption, Course
from django.utils.datetime_safe import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from io import StringIO
import time

@shared_task
def add_caption(course_id, row):


    if row["transcript_text"] != "":
        video_url = row["video_url"]
        transcript_url = row["transcript_url"]
        transcript_text = row["transcript_text"]
        transcript_timestamp = row["transcript_timestamp"]
        title = row["title"]
        owner = row["owner"]

        # Create video object if it doesn't exist
        try:
            video = Video.objects.get(video_url=video_url)
        except ObjectDoesNotExist:
            return "Video does not exist"
        except MultipleObjectsReturned:
            video = Video.objects.filter(video_url=video_url)[0]

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

    try:
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return "Course does not exists!"

    # convert dict to dataframe
    decoded_file = pd.DataFrame(decoded_file)

    # # Get rid of duplicates by columns video_url, title, date, time
    df = decoded_file.drop_duplicates(subset=['video_url', 'title', 'date', 'time'])

    for i, row in df.iterrows():
        try:
            video = Video.objects.get(video_url=df["video_url"])
        except ObjectDoesNotExist:
            print("Video does not exist, adding video")
            video = Video(
                course = course,
                video_url = row["video_url"],
                title = row["title"],
                date = datetime.strptime(row["date"], "%m/%d/%Y").date(),
                time = datetime.strptime(row["time"], "%I:%M %p").time()
            )
            video.save()
        except MultipleObjectsReturned:
            continue



    # # Let's create the captions
    for i, row in decoded_file.iterrows():
        # add delay of 0.5 sec
        time.sleep(0.5)
        
        add_caption.delay(course_id, row.to_dict())
    
    return "Done"


    

