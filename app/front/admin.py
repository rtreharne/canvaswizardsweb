from django.contrib import admin
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

from .models import Contact, Service, Event, Registration, Resource, Portfolio

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image', 'iframe', 'url', 'datetime', 'tool')
    search_fields = ('title', 'description', 'url')
    search_fields = ('title', 'description', 'url', 'tool')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_filter = ('date',)
    search_fields = ('name',)

class RegistrationAdmin(admin.ModelAdmin):

    list_display = ('last_name', 'first_name', 'event', 'present', 'event_date', 'mode',)
    list_filter = ('event', 'event__date', 'present', 'mode')
    search_fields = ('last_name', 'first_name', 'email')

    list_editable = ('present',)

    actions = ['export_to_csv']

    change_list_template = 'front/my_model_change_list.html'

    # event date field for the list view
    def event_date(self, obj):
        return obj.event.date
    
    # Want to make sure 'last_name' column is capitalized
    def last_name(self, obj):
        return obj.last_name.capitalize()
    

    event_date.short_description = 'Event Date'


    class Media:
        js = ('autosave.js',)

    # Build a custom action to export the selected registrations to a CSV file
    def export_to_csv(self, request, queryset):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=registrations.csv'
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Email', 'Event', 'Event Date', 'Mailing List'])
        for registration in queryset:
            writer.writerow([smart_str(registration.last_name), smart_str(registration.first_name), smart_str(registration.email), smart_str(registration.event), smart_str(registration.event.date), smart_str(registration.mailing_list)])
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
admin.site.register(Portfolio, PortfolioAdmin)

