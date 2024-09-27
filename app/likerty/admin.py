from django.contrib import admin
from .models import *

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('label', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('label',)

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'response', 'comment', 'created_at')
    list_filter = ('survey',)
    search_fields = ('survey', 'response')

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)



