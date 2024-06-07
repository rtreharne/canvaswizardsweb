from django.contrib import admin
from .models import OverviewProfile, OverviewRequest

class OverviewProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'downloads', 'max_downloads')
    search_fields = ('name', 'email')
    list_filter = ('downloads', 'max_downloads')
    list_editable = ('max_downloads',)


class OverviewRequestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'created', 'completed', 'downloaded')
    search_fields = ('profile__name', 'profile__email')
    list_filter = ('completed', 'downloaded')

admin.site.register(OverviewProfile, OverviewProfileAdmin)
admin.site.register(OverviewRequest, OverviewRequestAdmin)

