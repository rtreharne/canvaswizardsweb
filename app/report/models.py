from django.db import models
import uuid

class ReportProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def save(self, *args, **kwargs):
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ReportRequest(models.Model):
    profile = models.ForeignKey(ReportProfile, on_delete=models.CASCADE, null=True, blank=True)
    course_code = models.CharField(max_length=100, null=True, blank=True)
    assignment_name = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    log = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    file = models.FileField(upload_to='report/', null=True, blank=True)
    downloaded = models.BooleanField(default=False)

    def __str__(self):
        return self.profile.name