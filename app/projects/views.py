from django.shortcuts import render, redirect

from .models import *
from .forms import SupervisorForm, InstitutionForm, AdminDepartmentForm, SupervisorSetForm
from django.views import View
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt




def index(request):

    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            institution = form.cleaned_data['institution_name']
            user_type = form.cleaned_data['user_type']
            admin_department = form.cleaned_data['admin_department']

            if user_type == 'supervisor':

                # redirect to supervisor portal
                return redirect('projects:supervisor', institution_slug=institution.slug, admin_department_slug=admin_department.slug)

        
    form = InstitutionForm()

    return render(request, 'projects/index.html', {'form': form})


def supervisor_dash(request, institution_slug, admin_department_slug, supervisor_username):
    institution = Institution.objects.get(slug=institution_slug)
    supervisor = Supervisor.objects.get(username=supervisor_username, institution=institution)
    admin_department = Department.objects.get(slug=admin_department_slug)

    supervisor_sets = SupervisorSet.objects.filter(supervisor=supervisor)

    if request.method == 'POST':
        form = SupervisorSetForm(request.POST)
        if form.is_valid():
            available_for_ug = form.cleaned_data['available_for_ug']
            available_for_pg = form.cleaned_data['available_for_pg']
            project_keywords = form.cleaned_data['keywords']

            supervisor_set = form.save(commit=False)
            
            supervisor_set.available_for_ug = available_for_ug
            supervisor_set.available_for_pg = available_for_pg

            supervisor_set.save()

            supervisor_set.keywords.set(project_keywords)
        
            supervisor_sets = SupervisorSet.objects.filter(supervisor=supervisor)
            return redirect('projects:supervisor-dash', institution_slug=institution.slug, admin_department_slug=admin_department.slug, supervisor_username=supervisor.username)


        else:
            return redirect('projects:supervisor-dash', institution_slug=institution.slug, admin_department_slug=admin_department.slug, supervisor_username=supervisor.username)

    context = {
        'supervisor': supervisor,
        'institution': institution,
        'admin_department': Department.objects.get(slug=admin_department_slug),
        'form': SupervisorSetForm(initial={
            'supervisor': supervisor,
            'institution': institution,
            'admin_dept': admin_department,
        }),
        'supervisor_sets': supervisor_sets,
    }
    return render(request, 'projects/supervisor_dash.html', context)

def supervisors(request, institution_slug, admin_department_slug):

    if request.method == 'POST':
        form = SupervisorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower().replace(' ', '')
            department = form.cleaned_data['department']

            department = Department.objects.get(pk=department.id)
            # Look for the supervisor in the supervisors table
            # If they don't exist, return error message
            if not Supervisor.objects.filter(username=username, institution=department.institute.institution).exists():
                return render(request, 'projects/supervisors.html', {'error': 'Supervisor not found', 'form': SupervisorForm()})
            else:
                supervisor = Supervisor.objects.get(username=username, institution=department.institute.institution)

                if supervisor.department is None:
                    # set supervisor department to department.id
                    supervisor.department = Department.objects.get(pk=department.id)
                    supervisor.save()
                elif supervisor.department != department:
                    return render(request, 'projects/supervisors.html', {'error': 'Supervisor already assigned to a different department.', 'form': SupervisorForm()})
                
                return redirect(
                    'projects:supervisor-dash', 
                    institution_slug=institution_slug,
                    admin_department_slug=admin_department_slug,
                    supervisor_username=supervisor.username
                )

    else:
        form = SupervisorForm()

    context = {
        'form': form,
        'institution': Institution.objects.get(slug=institution_slug),
        'admin_department': Department.objects.get(slug=admin_department_slug),
    }
    return render(request, 'projects/supervisors.html', context)

class GetDepartmentsView(View):
    def get(self, request, *args, **kwargs):
        institute_pk = request.GET.get('institute_name', None)

        print(f'{institute_pk} is the institute name')
        print(f'{request.GET} is the request.GET')

        if institute_pk is not None:
            try:
                institute = Institute.objects.get(pk=institute_pk)
            except:
                return JsonResponse({'error': 'Invalid request'}, status=400)
            departments = Department.objects.filter(institute=institute)
            print(departments.values())
            return JsonResponse(list(departments.values()), safe=False)
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
class GetAdminDepartmentsView(View):
    def get(self, request, *args, **kwargs):
        institution_pk = request.GET.get('institution_name', None)
        
        if institution_pk is not None:
            try:
                institution = Institution.objects.get(pk=institution_pk)
            except:
                return JsonResponse({'error': 'Invalid request'}, status=400)
            admin_departments = set([x.department for x in Admin.objects.filter(institution=institution)])
            departments = Department.objects.filter(id__in=[x.id for x in admin_departments])
            return JsonResponse(list(departments.values()), safe=False)
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

@csrf_exempt
def delete_supervisor_set(request, supervisor_set_id):
    if request.method == 'DELETE':
        SupervisorSet.objects.get(id=supervisor_set_id).delete()
        return JsonResponse({'status': 'success'})
