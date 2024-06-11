from django.contrib import admin
from .models import Video, Caption, Course

class VideoAdmin(admin.ModelAdmin):
    list_display = ['video_url', 'date', 'time']
    search_fields = ['date', 'time',]

class CaptionAdmin(admin.ModelAdmin):
    list_display = ['transcript_text', 'transcript_timestamp', 'owner']
    search_fields = ['transcript_text',]
    list_filter = ['owner',]

admin.site.register(Video, VideoAdmin)
admin.site.register(Caption, CaptionAdmin)
admin.site.register(Course)

