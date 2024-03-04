from django.db import models
from django.utils.text import slugify

class Rule(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE, related_name='rules')
    year = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.title}'
    
class Pathway(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE, related_name='tribes')
    url = models.URLField(blank=True, null=True, max_length=1000)

    def __str__(self):
        return f'{self.title}'

class Module(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=128)
    semester = models.CharField(max_length=28)
    level = models.CharField(max_length=28)
    credits = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    in_programmes = models.ManyToManyField('Programme', related_name='programmes')
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    compulsory = models.BooleanField(default=False)
    practical = models.BooleanField(default=False)
    year = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.code}'
    
class Programme(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)
    visible = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            while Programme.objects.filter(slug=slug).exists():
                slug = "{}-{}".format(slug, Programme.objects.filter(slug__startswith=slug).count())
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'
    