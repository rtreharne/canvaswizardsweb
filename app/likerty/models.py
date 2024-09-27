from django.db import models
from django.utils.text import slugify

class Survey(models.Model):
    label = models.CharField(max_length=100, unique=True)

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    question = models.CharField(max_length=500, null=True, blank=True)

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    comments_on = models.BooleanField(default=True)

    responses_viewable = models.BooleanField(default=True)
    feedback_viewable = models.BooleanField(default=True)

    redirect_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    # create slug from label using slugify and ensure uniqueness
    def save(self, *args, **kwargs):
        # create slug from label using slugify
        try:
            self.slug = slugify(self.label)

            if self.slug == "create":
                self.slug == "create-x"
            # ensure uniqueness
            while Survey.objects.filter(slug=self.slug).exists():
                self.slug = slugify(self.slug + '-' + str(Survey.objects.count()))
        except Exception as e:
            print(e)
        super(Survey, self).save(*args, **kwargs)
            

    def __str__(self):
        return self.label
    

class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    # Likert scale response
    response = models.IntegerField()

    comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.IntegerField(default=0)

    dislikes = models.IntegerField(default=0)

    abuse = models.IntegerField(default=0)

    hidden = models.BooleanField(default=False)


    def __str__(self):
        return self.survey.label
