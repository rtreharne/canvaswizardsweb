from django.contrib import admin
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

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

    actions = ['export_to_csv']

    # Build a custom action to export the selected registrations to a CSV file
    def export_to_csv(self, request, queryset):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=registrations.csv'
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Email', 'Event', 'Event Date'])
        for registration in queryset:
            writer.writerow([smart_str(registration.last_name), smart_str(registration.first_name), smart_str(registration.email), smart_str(registration.event), smart_str(registration.event.date)])
        return response
    
    
    export_to_csv.short_description = 'Export to CSV'


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name', 'url')


admin.site.register(Contact, ContactAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Resource, ResourceAdmin)    
