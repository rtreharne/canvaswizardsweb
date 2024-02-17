from django.db import models

class Portfolio(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.FileField(upload_to='portfolio/')
    iframe = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
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
    online_info = models.TextField(null=True, blank=True)
    resources = models.URLField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    iframe = models.TextField(null=True, blank=True)
    registrations = models.IntegerField(default=0)
    registrations_online = models.IntegerField(default=0)
    reddit = models.URLField(null=True, blank=True)
    playlist = models.URLField(null=True, blank=True)
    in_progress = models.BooleanField(default=False)
    fully_booked = models.BooleanField(default=False)
    ask_for_track = models.BooleanField(default=False)
    ask_for_description = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Contact(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    message = models.TextField(help_text="How can I help? Please provide as much detail as possible.")
    mailing = models.BooleanField(default=False, verbose_name="Receive updates on my work and events?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.last_name
    
class Registration(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.CharField(max_length=100, null=True, blank=True)

    CHOICES = [
        ('In Person', 'In Person'),
        ('Online', 'Online')
    ]
    mode = models.CharField(max_length=100, null=True, blank=True, default="In Person", choices=CHOICES, verbose_name="How will you attend?", help_text="(If you choose 'In Person' then you can still attend online if you need to.)")
    
    track = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name="What's your issue?", help_text="Please describe your issue in as much detail as possible. The more we know, the better we can help you.")

    
    mailing_list = models.BooleanField(default=False, verbose_name="Join our mailing list for info on future events?")
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Resource(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    events = models.ManyToManyField(Event, blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)


    def __str__(self):
        return self.name
