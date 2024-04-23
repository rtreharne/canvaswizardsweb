from django.contrib import admin
from .models import *
from django.contrib import messages

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

class PrerequisiteAdmin(AdminBase):
    list_display = ('name',)
    search_fields = ('name',)

class ProjectTypeAdmin(AdminBase):
    list_display = ('name',)
    search_fields = ('name',)

class ProjectKeywordAdmin(AdminBase):
    list_display = ('name',)
    search_fields = ('name',)

class SupervisorSetsAdmin(AdminBase):
    list_display = (
        'supervisor',
        'type',
        'kw', 
        'available_for_ug',
        'available_for_pg',
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
    
    list_filter = ('round', 'active', 'ug_or_pg')
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
