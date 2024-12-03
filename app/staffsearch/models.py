from django.db import models
from helpers.models import TrackingModel

class Institute(TrackingModel):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Directorate(TrackingModel):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Department(TrackingModel):
    name = models.CharField(max_length=256, unique=True)
    institute = models.ForeignKey(Institute, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class Profile(TrackingModel):
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256)

    role = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    url = models.URLField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    about = models.TextField(blank=True, null=True)
    research = models.TextField(blank=True, null=True)
    teaching = models.TextField(blank=True, null=True)
    publications = models.TextField(blank=True, null=True)
    professional_activities = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.last_name

class Keyword (TrackingModel):
    keyword = models.CharField(max_length = 128)
    score = models.FloatField(default=0)
    frequency = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.keyword

class Banner(TrackingModel):
    url = models.URLField(default="https://github.com/rtreharne/staff-search-static/blob/main/University%20of%20Liverpool%20campus%20010621%200040.JPG?raw=true")

    def __str__(self):
        return self.url
    
class Root(TrackingModel):
    url = models.URLField(null=True, blank=True, default="https://liverpool.ac.uk", unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.url
    
class Search(TrackingModel):
    keywords = models.CharField(max_length = 1000, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Searches"

    def __str__(self):
        return self.keywords

