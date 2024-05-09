from django.db import models
from projects.models import Supervisor

# Create your models here.
class Module(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    credits = models.IntegerField(null=True, blank=True)
    level = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code}"
    
class LearningObjective(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=100, default="LO")
    description = models.TextField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.description

class Response(models.Model):
    staff = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    learning_objective = models.ForeignKey(LearningObjective, on_delete=models.CASCADE)
    additional_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.created_at)