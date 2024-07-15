from django.db import models
import uuid

class PresentationProfile(models.Model):
    name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    used = models.IntegerField(default=0)
    max_use = models.IntegerField(default=20)

    def __str__(self):
        return self.name


class PresentationRequest(models.Model):
    profile = models.ForeignKey(PresentationProfile, on_delete=models.CASCADE, null=True, blank=True)
    course_code = models.CharField(max_length=100, null=True, blank=True)
    assignment_name = models.CharField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    log = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    html = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.profile.name