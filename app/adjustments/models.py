from django.db import models
import uuid

class AdjustmentProfile(models.Model):
    name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    downloads = models.IntegerField(default=0)
    max_downloads = models.IntegerField(default=10000)

    def save(self, *args, **kwargs):
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class AdjustmentRequest(models.Model):
    profile = models.ForeignKey(AdjustmentProfile, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    log = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    file = models.FileField(upload_to='adjustments/', null=True, blank=True)
    downloaded = models.BooleanField(default=False)
    from_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.profile.name

    
