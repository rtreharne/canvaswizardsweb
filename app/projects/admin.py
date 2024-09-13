from django.contrib import admin
from .models import *
from django.contrib import messages
from .forms import CsvImportForm
import csv
from django.shortcuts import render, redirect
from django.urls import path, include, reverse
from django.http import HttpResponse
import datetime
from .tasks import allocate
from django.utils.html import format_html
from django.utils.safestring import mark_safe


from django.contrib.admin import SimpleListFilter

class UndersupplyFilter(SimpleListFilter):
    title = 'undersupply'
    parameter_name = 'undersupply'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(id__in=[
                obj.id for obj in queryset if self.model_admin.undersupply(obj)
            ])
        if self.value() == 'no':
            return queryset.exclude(id__in=[
                obj.id for obj in queryset if self.model_admin.undersupply(obj)
            ])
        return queryset

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.model_admin = model_admin

class AdminBase(admin.ModelAdmin):
    readonly_fields = ('institution', 'admin_dept')

    # Only show records that belong to the admin's department
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            admin = Admin.objects.get(user=request.user)
            return qs.filter(admin_dept=admin.department)
        except Admin.DoesNotExist:
            messages.error(request, "Admin object does not exist for this user.")
            return qs
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return qs

    def save_model(self, request, obj, form, change):
        try:
            admin = Admin.objects.get(user=request.user)
            obj.admin_dept = admin.department
            obj.institution = admin.institution
        except Admin.DoesNotExist:
            messages.error(request, "Admin object does not exist for this user.")
            return
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return

        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            messages.error(request, f"An error occurred when saving the model: {e}")


class ProgrammeAdmin(AdminBase):
    list_display = ('name', 'admin_dept')
    list_filter = ('admin_dept',)


class LocationAdmin(AdminBase):
    list_display = ('name', 'admin_dept')
    list_filter = ('admin_dept',)
    search_fields = ('name',)

class SupervisorAdmin(AdminBase):
    list_display = ('username', 'last_name', 'email', 'department', 'projects_UG', 'projects_PG', 'active', 'undersupply_link')
    list_filter = ('department', 'active', UndersupplyFilter,)
    search_fields = ('username', 'last_name', 'first_name', 'email')
    list_editable = ('projects_UG', 'projects_PG', 'active')

    actions = ['export_csv']

    change_list_template = "projects/supervisors_changelist.html"

    # create 'undersupply' column that is calculated

    def undersupply(self, obj):
        # get all related supervisor sets using the supervisor
        sets = SupervisorSet.objects.filter(supervisor=obj)

        # sum all of the available_for_ug
        ug = sum([set.available_for_ug for set in sets])

        # return True if the sum is less than the projects_UG
        return ug < obj.projects_UG
    
    def undersupply_link(self, obj):
        if self.undersupply(obj):
            url = reverse('admin:projects_supervisorset_changelist') + f'?supervisor={obj.id}'
            return format_html('<a href="{}" target="_blank">Yes</a>', url)
        else:
            return 'No'
    undersupply_link.short_description = 'Undersupply'  # Column header name
    undersupply_link.allow_tags = True  # Allow HTML tags

    
    

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    def import_csv(self, request):

        payload = {}

        payload["headers"] = "You must use the following headers: last_name, first_name, projects_UG, projects_PG, max_projects, username, email,"
        
        if request.method == "POST":

            form = CsvImportForm(request.POST, request.FILES)

            payload["form"] = form

            if form.is_valid():

                admin = Admin.objects.get(user=request.user)

                admin_department = admin.department
                institution = admin.institution
                
                # read csv file
                csv_file = request.FILES["file"]
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)

                # check if headers are correct
                headers = reader.fieldnames
                if headers != ["last_name", "first_name", "projects_UG", "projects_PG", "max_projects", "username", "email"]:
                    payload["error"] = "Incorrect headers. Please use the following headers: last_name, first_name, username, email"
                    return render(request, "forms/csv_form.html", payload)
                
                # create supervisor objects
                error_string = ""
                for row in reader:
                    supervisor = Supervisor(
                        last_name=row["last_name"],
                        first_name=row["first_name"],
                        username=row["username"],
                        projects_UG=row["projects_UG"],
                        projects_PG=row["projects_PG"],
                        email=row["email"],
                        admin_dept=admin_department,
                        institution=institution,
                        active=False
                    )
                    try:
                        supervisor.save()
                    except:
                        error_string += f"Error creating supervisor: {row['last_name']}.\n"

            else:
                print("form not valid", form.errors)
                return render(request, "forms/csv_form.html", payload)

            self.message_user(request, "Your csv file has been imported. Your supervisors will appear shortly. Keep refreshing.")

            if error_string:
                self.message_user(request, error_string)
            
            print("redirecting")
            return redirect("..")
        
        form = CsvImportForm()
        payload["form"] = form

        return render(
            request, "forms/csv_form.html", payload
        )
    
    def export_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                row.append(getattr(obj, field, ''))
            try:
                writer.writerow(row)
            except:
                continue

        return response

    export_csv.short_description = "Export Selected to CSV"
    


class AdminAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'email', 'department', 'institution')
    list_filter = ('department', 'institution')
    search_fields = ('last_name', 'first_name', 'email')

class RoundAdmin(AdminBase):
    list_display = ('name', 'slug', 'start_date', 'end_date')
    list_filter = ('name',)
    search_fields = ('name',)

class StudentAdmin(AdminBase):
    list_display = ('student_id', 'last_name', 'first_name', 'active', 'email', 'programme', 'mbiolsci', 'project_keywords', 'project_types', 'priority', 'allocation_round', 'submitted_at')
    list_filter = ('programme', 'mbiolsci', 'allocation_round', 'priority')
    search_fields = ('last_name', 'first_name', 'email')
    actions = ['export_csv']
    list_editable = ('active',)

    # Default filter by most recent allocation round
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            admin = Admin.objects.get(user=request.user)
            return qs.filter(allocation_round=Round.objects.filter(institution=admin.institution, admin_dept=admin.department).last())
        except Admin.DoesNotExist:
            messages.error(request, "Admin object does not exist for this user.")
            return qs
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return qs
        
    def export_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                row.append(getattr(obj, field, ''))
            try:
                writer.writerow(row)
            except:
                continue

        return response

    export_csv.short_description = "Export Selected to CSV"

class PrerequisiteAdmin(AdminBase):
    list_display = ('name',)
    search_fields = ('name',)

    change_list_template = "projects/courses_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    def import_csv(self, request):

        payload = {}

        payload["headers"] = "You must use the following headers: course"
        
        if request.method == "POST":

            form = CsvImportForm(request.POST, request.FILES)

            payload["form"] = form

            print("courses form", form)

            if form.is_valid():

                admin = Admin.objects.get(user=request.user)

                admin_department = admin.department
                institution = admin.institution
                
                # read csv file
                csv_file = request.FILES["file"]
                decoded_file = csv_file.read().decode("latin-1").splitlines()
                reader = csv.DictReader(decoded_file)

                # check if headers are correct
                headers = reader.fieldnames
                if headers != ["course"]:
                    payload["error"] = "Incorrect headers. Please use the following headers: course"
                    return render(request, "forms/csv_form.html", payload)
                
                # create supervisor objects

                error_string = ""
                for row in reader:
                    print(row["course"])
                    try:
   
                        prerequisite = Prerequisite(
                            name = row["course"].strip().upper(),
                            
                            admin_dept=admin_department,
                            institution=institution

                        )

                        prerequisite.save()

                    except:
                        error_string += f"Error adding course: {row['course']}.\n"
                        

            else:
                print("form not valid", form.errors)
                return render(request, "forms/csv_form.html", payload)

            self.message_user(request, "Your csv file has been imported. Your courses will appear shortly. Keep refreshing.")

            if error_string:
                self.message_user(request, error_string)
            
            print("redirecting")
            return redirect("..")
        
        form = CsvImportForm()
        payload["form"] = form

        return render(
            request, "forms/csv_form.html", payload
        )

class ProjectTypeAdmin(AdminBase):
    list_display = ('name',)
    search_fields = ('name',)
    
class ProjectKeywordAdmin(AdminBase):
    list_display = ('name','department','description', 'institute', 'ug_only', 'pg_only')
    search_fields = ('name',)
    actions = ['export_csv']

    # include description in list_display but truncate to 20 characters
    def description(self, obj):
        return obj.description[:20]


    change_list_template = "projects/keywords_changelist.html"


    def institute(self, obj):
        try:
            return obj.department.institute.name
        except:
            return ""

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    def import_csv(self, request):

        payload = {}

        payload["headers"] = "You must use the following headers: keyword"
        
        if request.method == "POST":

            form = CsvImportForm(request.POST, request.FILES)

            payload["form"] = form

            print("keywords form", form)

            if form.is_valid():

                admin = Admin.objects.get(user=request.user)

                admin_department = admin.department
                institution = admin.institution
                
                # read csv file
                csv_file = request.FILES["file"]
                decoded_file = csv_file.read().decode("latin-1").splitlines()
                reader = csv.DictReader(decoded_file)

                # check if headers are correct
                headers = reader.fieldnames
                if headers != ["keyword", "description", "department"]:
                    payload["error"] = "Incorrect headers. Please use the following headers: keyword, description, department"
                    return render(request, "forms/csv_form.html", payload)
                
                # create supervisor objects

                error_string = ""
                for row in reader:
                    print(row["keyword"])
                    institutes = Institute.objects.filter(institution = institution)
                    try:
                        department_slug = row["department"].strip().lower()
                        keyword = ProjectKeyword(
                            name = row["keyword"].strip().capitalize(),
                            
                            admin_dept=admin_department,
                            institution=institution,
                            description = row["description"].strip(),
                            department = Department.objects.get(slug=department_slug, institute__in=institutes)
                        )


                        keyword.save()
                    except:
                        error_string += f"Error creating keyword: {row['keyword']}.\n"

            else:
                print("form not valid", form.errors)
                return render(request, "forms/csv_form.html", payload)

            self.message_user(request, "Your csv file has been imported. Your courses will appear shortly. Keep refreshing.")

            if error_string:
                self.message_user(request, error_string)
            
            print("redirecting")
            return redirect("..")
        
        form = CsvImportForm()
        payload["form"] = form

        return render(
            request, "forms/csv_form.html", payload
        )
    
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

class SupervisorSetsAdmin(AdminBase):
    list_display = (
        'supervisor',
        'type',
        'kw', 
        'available_for_ug',
        'available_for_pg',
        'prerequisite',
        'active'
    )
    search_fields = ('supervisor__username',)

    list_editable = ('active', 'available_for_ug', 'available_for_pg')

    actions = ['export_csv']

    def kw(self, obj):
        keywords = [str(keyword.name) for keyword in obj.keywords.all()]
        return keywords


    # rename kw
    kw.short_description = 'Keywords'

    def export_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields] + ['keywords']
        print("FIELD NAMES:", field_names)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                if field == 'keywords':
                    keywords = obj.keywords.all()
                    keywords_str = ', '.join([keyword.name for keyword in keywords])
                    row.append(keywords_str)
                else:
                    row.append(getattr(obj, field, ''))
            try:
                writer.writerow(row)
            except:
                continue

        return response

    export_csv.short_description = "Export Selected to CSV"

class ProjectAdmin(AdminBase):
    list_display = (
        'primary_supervisor',
        'second_supervisor',
        'round',
        'kw_set',
        'type',
        'ug_or_pg',
        'active',
        )
    
    actions = ['export_csv']
    
    list_filter = ('round', 'active', 'ug_or_pg', 'active')
    list_editable = ('active',)
    search_fields = ('supervisor_set__supervisor__first_name', 'supervisor_set__supervisor__last_name')
    
    def primary(self, obj):
         return f'{obj.supervisor_set.supervisor.last_name}, {obj.supervisor_set.supervisor.first_name}'
    
    def kw_set(self, obj):
        keywords = [str(keyword.name) for keyword in obj.supervisor_set.keywords.all()]
        return keywords
    kw_set.short_description = 'Keywords'

    def type(self, obj):
        return obj.supervisor_set.type.name
    
    def export_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields] + ['keywords', 'type']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                if field == 'keywords':
                    keywords = obj.supervisor_set.keywords.all()
                    keywords_str = ', '.join([keyword.name for keyword in keywords])
                    row.append(keywords_str)
                elif field == 'type':
                    row.append(obj.supervisor_set.type if obj.supervisor_set else '')
                else:
                    row.append(getattr(obj, field, ''))
            try:
                writer.writerow(row)
            except:
                continue

        return response

    export_csv.short_description = "Export Selected to CSV"

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'institute')
    list_filter = ('institute',)
    search_fields = ('name',)

class AllocationAdmin(admin.ModelAdmin):
    list_display = ('round', 'user', 'status', 'created_at', 'output')
    list_filter = ('round', 'status', 'user')

    # read only fields
    readonly_fields = ('user', 'status', 'created_at', 'output')

    # When adding a new allocation I only want user to see Round field
    def add_view(self, request, form_url='', extra_context=None):
        self.fields = ('round',)
        return super().add_view(request, form_url, extra_context)
    
    

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set the user during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)
        allocate.delay(obj.id)
        


admin.site.register(Institution)
admin.site.register(Institute)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Prerequisite, PrerequisiteAdmin)
admin.site.register(Supervisor, SupervisorAdmin)
admin.site.register(SupervisorSet, SupervisorSetsAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(ProjectKeyword, ProjectKeywordAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Allocation, AllocationAdmin)

# Register your models here.
