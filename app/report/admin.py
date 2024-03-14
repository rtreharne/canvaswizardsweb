from django.contrib import admin
from .models import ReportRequest, ReportProfile

class ReportProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created')
    search_fields = ('name', 'email')


class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'created', 'completed', 'downloaded')
    search_fields = ('profile__name', 'profile__email')
    list_filter = ('completed', 'downloaded')

admin.site.register(ReportProfile, ReportProfileAdmin)
admin.site.register(ReportRequest, ReportRequestAdmin)



