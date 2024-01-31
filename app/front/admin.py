from django.contrib import admin

from .models import Contact, Service, Event, Registration, Resource

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_filter = ('date',)
    search_fields = ('name',)

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'event', 'created_at')
    list_filter = ('event', 'created_at')
    search_fields = ('last_name', 'first_name', 'email')

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name', 'url')


admin.site.register(Contact, ContactAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Resource, ResourceAdmin)    
