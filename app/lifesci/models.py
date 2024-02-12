from django.db import models
from front.models import Event

class preloaded_user(models.Model):
    
    user_id = models.BigIntegerField()

    def __str__(self):
        return f"{self.user_id}"



class Human(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='life_sci_user')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Question(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    pub_date = models.DateTimeField('date published')
    previous = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    next = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='next_question')
    question_success = models.TextField()
    image = models.FileField(upload_to='questions/', null=True, blank=True)
    function_name = models.CharField(max_length=200, null=True, blank=True)
    reddit = models.URLField(null=True, blank=True)
    resources = models.URLField(null=True, blank=True)
    puzzle_input = models.BooleanField(default=True)
    example_answer = models.BigIntegerField(null=True, blank=True)
    figure_example = models.FileField(upload_to='questions/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title}"
    
class Answer(models.Model):
    human = models.ForeignKey(Human, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='life_sci_event')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)
    time_submitted = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    submitted = models.BigIntegerField(default=0)
    figure = models.FileField(upload_to='answers/', null=True, blank=True)

    def __str__(self):
        return f"{self.human} - {self.question} - {self.correct}"
    
class Resource(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name}"




    