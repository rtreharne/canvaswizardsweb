from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.FileField(upload_to='icons/')

    def __str__(self):
        return self.name
    
class Event(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    image = models.FileField(upload_to='events/')
    location = models.CharField(max_length=100)
    resources = models.URLField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='What service are you interested in?')
    email = models.EmailField()
    message = models.TextField()
    mailing = models.BooleanField(default=False, verbose_name="Join our mailing list?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Registration(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
