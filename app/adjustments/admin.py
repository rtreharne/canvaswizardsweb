from django.contrib import admin
from .models import AdjustmentRequest, AdjustmentProfile

class AdjustmentProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'downloads', 'max_downloads')
    search_fields = ('name', 'email')
    list_filter = ('downloads', 'max_downloads')
    list_editable = ('max_downloads',)


class AdjustmentRequestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'created', 'completed', 'downloaded')
    search_fields = ('profile__name', 'profile__email')
    list_filter = ('completed', 'downloaded')

admin.site.register(AdjustmentProfile, AdjustmentProfileAdmin)
admin.site.register(AdjustmentRequest, AdjustmentRequestAdmin)


