from django.contrib import admin

from .models import Human, Question, Answer, Resource

class HumanAdmin(admin.ModelAdmin):

    list_display = ("first_name", "last_name", "slug")
    search_fields = ["first_name", "last_name", "slug"]

class QuestionAdmin(admin.ModelAdmin):

    list_display = ("title", "text", "pub_date", "previous", "next", "question_success")
    search_fields = ["title", "text", "pub_date", "previous", "next", "question_success"]

class AnswerAdmin(admin.ModelAdmin):
    
        list_display = ("human_slug", "event", "question", "correct", "time_submitted", "score", "submitted")
        search_fields = ["human_slug", "event", "question", "correct", "time_submitted", "score"]

        # add human.slug to list_display
        def human_slug(self, obj):
            return obj.human.slug
        
class ResourceAdmin(admin.ModelAdmin):
         
        list_display = ("name", "url", "question")
        search_fields = ["name", "url", "question"]

        

  
admin.site.register(Human, HumanAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Resource, ResourceAdmin)