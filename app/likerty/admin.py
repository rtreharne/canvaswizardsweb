from django.contrib import admin
from .models import *
from django.http import HttpResponse
import datetime
import csv

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('label', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('label',)

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'response', 'comment', 'created_at')
    list_filter = ('survey',)
    search_fields = ('survey', 'response')

    actions = ["export_csv"]

    def export_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')

        # Create timestamp string for filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fname = f"{timestamp}_keywords.csv"
        

        response['Content-Disposition'] = f'attachment; filename={fname}'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_csv.short_description = 'Export to CSV'

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)



