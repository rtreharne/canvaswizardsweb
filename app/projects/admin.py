from django.contrib import admin
from .models import *
from django.contrib import messages
from .forms import CsvImportForm
import csv
from django.shortcuts import render, redirect
from django.urls import path, include, reverse



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
    list_display = ('username', 'last_name', 'email', 'department', 'projects_UG', 'projects_PG', 'active')
    list_filter = ('department',)
    search_fields = ('username', 'last_name', 'first_name', 'email')
    list_editable = ('projects_UG', 'projects_PG', 'active')

    change_list_template = "projects/supervisors_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    def import_csv(self, request):

        payload = {}

        payload["headers"] = "You must use the following headers: last_name, first_name, username, email"
        
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
                if headers != ["last_name", "first_name", "username", "email"]:
                    payload["error"] = "Incorrect headers. Please use the following headers: last_name, first_name, username, email"
                    return render(request, "forms/csv_form.html", payload)
                
                # create supervisor objects
                error_string = ""
                for row in reader:
                    supervisor = Supervisor(
                        last_name=row["last_name"],
                        first_name=row["first_name"],
                        username=row["username"],
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
    


class AdminAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'email', 'department', 'institution')
    list_filter = ('department', 'institution')
    search_fields = ('last_name', 'first_name', 'email')

class RoundAdmin(AdminBase):
    list_display = ('name', 'slug', 'start_date', 'end_date')
    list_filter = ('name',)
    search_fields = ('name',)

class StudentAdmin(AdminBase):
    list_display = ('student_id', 'last_name', 'first_name', 'email', 'programme', 'allocation_round')
    list_filter = ('programme', 'allocation_round')
    search_fields = ('last_name', 'first_name', 'email')

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
    list_display = ('name','department','institute', 'ug_only', 'pg_only')
    search_fields = ('name',)

    change_list_template = "projects/keywords_changelist.html"

    def institute(self, obj):
        return obj.department.institute.name

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
    search_fields = ('supervisor',)

    list_editable = ('active', 'available_for_ug', 'available_for_pg')

    def kw(self, obj):
        keywords = [str(keyword.name) for keyword in obj.keywords.all()]
        return keywords


    # rename kw
    kw.short_description = 'Keywords'

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


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'institute')
    list_filter = ('institute',)
    search_fields = ('name',)

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

# Register your models here.
