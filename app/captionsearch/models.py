from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=128, unique=True)
    url = models.URLField()

    def __str__(self):
        return self.name

class Video(models.Model):
    video_url = models.URLField()
    title = models.CharField(max_length=1000, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return self.video_url

class Caption(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, null=True)
    owner = models.CharField(max_length=128, blank=True, null=True)
    transcript_url = models.URLField()
    transcript_text = models.TextField()
    transcript_timestamp = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.transcript_text
    
class CaptionJob(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='caption_jobs/')
    datestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course.name

