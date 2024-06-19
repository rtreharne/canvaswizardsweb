from django.db import models

class Data(models.Model):
    label = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='sample/')
    open_at = models.DateTimeField(null=True, blank=True)
    close_at = models.DateTimeField(null=True, blank=True)
    sample_size = models.IntegerField()
    pin = models.IntegerField()


    def __str__(self):
        return self.label
