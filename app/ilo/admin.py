from django.contrib import admin
from .models import Module, LearningObjective, Response
from django.urls import path
from django.shortcuts import render, redirect
from projects.forms import CsvImportForm
import csv
import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import datetime

class AlphabeticalUsernameFilter(admin.SimpleListFilter):
    title = _('username')  # a label for this filter
    parameter_name = 'username'  # you can put here any name

    def lookups(self, request, model_admin):
        staffs = model_admin.model.objects.order_by('staff__username').values_list('staff__id', 'staff__username').distinct()
        return sorted([(id, username) for id, username in staffs], key=lambda x: x[1])  # sort by username

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(id__exact=self.value())
        else:
            return queryset


class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code',]

class LearningObjectiveAdmin(admin.ModelAdmin):
    list_display = ['module', 'label', 'module', 'truncated_description']
    search_fields = ['module', 'label', 'module', 'description', 'additional_info']

    # Truncate description
    def truncated_description(self, obj):
        if len(obj.description) > 50:
            return obj.description[:50] + ' ...'
        return obj.description
    
    truncated_description.short_description = 'Description'

    change_list_template = "ilo/learning_objective_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    def import_csv(self, request):

        payload = {}

        payload["headers"] = "You must use the following headers: module_short_name, module_code, label, description, additional_info"
        
        if request.method == "POST":

            form = CsvImportForm(request.POST, request.FILES)

            payload["form"] = form

            if form.is_valid():
                
                # read csv file
                csv_file = request.FILES["file"]
                decoded_file = csv_file.read().decode("latin-1").splitlines()
                reader = csv.DictReader(decoded_file)

                # check if headers are correct
                headers = reader.fieldnames
                if headers != ["module_short_name", "module_code", "type", "label", "description", "additional_info"]:
                    payload["error"] = "Incorrect headers. Please use the following headers: headers: module_chort_name, module_code, label, description, additional_info"
                    return render(request, "forms/csv_form.html", payload)
                
                # create supervisor objects
                error_string = ""
                for row in reader:
                    print(row)
                
                    # if module does not exist
                    try:
                        module = Module.objects.get(code=row["module_code"])
                    except Module.DoesNotExist:
                        module = Module(
                            name=row["module_short_name"], 
                            code=row["module_code"]
                        )
                        module.save()
                        continue

                    try:
                        if row["module_code"] != "":
                            lo = LearningObjective(
                                module=module,
                                type=row["type"],
                                label=row["label"],
                                description=row["description"],
                                additional_info=row["additional_info"]
                            )
                            lo.save()
                    except:
                        error_string += f"Error creating LO: {row['module_code']}.\n"
                        continue


                
                #     except:
                #         

            else:
                print("form not valid", form.errors)
                return render(request, "forms/csv_form.html", payload)

            self.message_user(request, "Your csv file has been imported. Your learning objectives will appear shortly. Keep refreshing.")

            if error_string:
                self.message_user(request, error_string)
            
            print("redirecting")
            return redirect("..")
        
        form = CsvImportForm()
        payload["form"] = form

        return render(
            request, "forms/csv_form.html", payload
        )
    
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['username', 'sortable_name', 'module', 'truncated_description', 'additional_info', 'active']
    search_fields = ['staff__username', 'learning_objective__module__code',]
    list_filter = ['active', AlphabeticalUsernameFilter,]
    ordering = ['staff']

    def username(self, obj):
        return obj.staff.username
    
    username.short_description = 'username'

    def sortable_name(self, obj):
        return f"{obj.staff.last_name}, {obj.staff.first_name}"

    # I want to create a custom action that exports selected responses to a csv file
    def export_to_csv(self, request, queryset):

        response = HttpResponse(content_type='text/csv')

        # create timestamped file name string
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_ilo_responses.csv"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['username', 'sortable_name', 'email', 'staff_institute', 'staff_department', 'module', 'LO', 'additional_info', 'active', 'date_created', 'date_updated'])

        for obj in queryset:
            writer.writerow([obj.staff.username, f"{obj.staff.last_name}, {obj.staff.first_name}", obj.staff.email, obj.staff.department, obj.staff.department.institute, obj.learning_objective.module.code, obj.learning_objective.description, obj.learning_objective.additional_info, obj.active, obj.created_at, obj.updated_at])

        return response
    
    export_to_csv.short_description = "Export selected to CSV"

    actions = [export_to_csv]





    def module(self, obj):
        return obj.learning_objective.module.code
    
    # truncat learning objective description
    def truncated_description(self, obj):
        if len(obj.learning_objective.description) > 50:
            return obj.learning_objective.description[:50] + ' ...'
        return obj.learning_objective.description
    
    # Make list sortable by module.code
    module.admin_order_field = 'learning_objective__module__code'

    
admin.site.register(Module, ModuleAdmin)
admin.site.register(LearningObjective, LearningObjectiveAdmin)
admin.site.register(Response, ResponseAdmin)