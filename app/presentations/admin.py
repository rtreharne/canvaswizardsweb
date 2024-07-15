from django.contrib import admin
from .models import PresentationRequest, PresentationProfile

class PresentationProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'used', 'max_use')
    search_fields = ('name', 'email')
    list_filter = ('used', 'max_use')
    list_editable = ('max_use',)


class PresentationRequestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'created', 'completed', 'uuid')
    search_fields = ('profile__name', 'profile__email')
    list_filter = ('completed',)

admin.site.register(PresentationProfile, PresentationProfileAdmin)
admin.site.register(PresentationRequest, PresentationRequestAdmin)



