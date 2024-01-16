from django.contrib import admin

from .models import Human, Question, Answer

class HumanAdmin(admin.ModelAdmin):

    list_display = ("first_name", "last_name", "slug")
    search_fields = ["first_name", "last_name", "slug"]

class QuestionAdmin(admin.ModelAdmin):

    list_display = ("title", "text", "pub_date", "previous", "next", "question_success")
    search_fields = ["title", "text", "pub_date", "previous", "next", "question_success"]

class AnswerAdmin(admin.ModelAdmin):
    
        list_display = ("human", "event", "question", "correct", "time_submitted", "score")
        search_fields = ["human", "event", "question", "correct", "time_submitted", "score"]
  
admin.site.register(Human, HumanAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)