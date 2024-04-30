from django.shortcuts import render, redirect

from .models import *
from .forms import SupervisorForm, InstitutionForm, AdminDepartmentForm, SupervisorSetForm, StudentForm
from django.views import View
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import IntegrityError


class GetKeywordsView(View):
    def get(self, request, *args, **kwargs):
        programme_id = request.GET.get('programme_id', None)
        keywords = ProjectKeyword.objects.exclude(exclude_programmes__id=programme_id).values('id', 'name')
        keyword_list = list(keywords)
        return JsonResponse(keyword_list, safe=False)



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

            if user_type == 'student':
                return redirect('projects:students', institution_slug=institution.slug, admin_department_slug=admin_department.slug)
        
    form = InstitutionForm()

    return render(request, 'projects/index.html', {'form': form})


def supervisor_dash(request, institution_slug, admin_department_slug, supervisor_username):
    institution = Institution.objects.get(slug=institution_slug)
    admin_department = Department.objects.get(slug=admin_department_slug),

    try:
        supervisor = Supervisor.objects.get(username=supervisor_username, institution=institution)
    except:
        return redirect('projects:supervisor', institution_slug=institution_slug, admin_department_slug=admin_department_slug)

    admin_department = Department.objects.get(slug=admin_department_slug)

    supervisor_sets = SupervisorSet.objects.filter(supervisor=supervisor)

    context = {
        'supervisor': supervisor,
        'institution': institution,
        'admin_department': admin_department,
        'supervisor_sets': supervisor_sets,
    }

    context['form'] = SupervisorSetForm(initial={
                'supervisor': supervisor,
                'institution': institution,
                'admin_dept': admin_department,
    })

    # Get latest round for department
    latest_round = Round.objects.filter(department=admin_department).order_by('-start_date').first()

    if latest_round is not None:
        context['latest_round'] = latest_round
        # if date of round close is not in the past, allow supervisor to add projects
        if latest_round.end_date >= timezone.now().date() >= latest_round.start_date:
            context['round_open'] = True
    



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
            context['form'] = form
            context['error'] = 'There is an error in the form. Please check the fields and try again.'
    
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
    

def students(request, institution_slug, admin_department_slug):
    institution = Institution.objects.get(slug=institution_slug)
    admin_department = Department.objects.get(slug=admin_department_slug)

    # get current round based on admin_department
    round = Round.objects.filter(department=admin_department).order_by('-start_date').first()

    

    if round.number_of_types < len(ProjectType.objects.filter(admin_dept=admin_department)):
        number_of_types = round.number_of_types
    else:
        number_of_types = len(ProjectType.objects.filter(admin_dept=admin_department))

    if round.number_of_keywords < len(ProjectKeyword.objects.filter(admin_dept=admin_department)):
        number_of_keywords = round.number_of_keywords
    else:
        number_of_keywords = len(ProjectKeyword.objects.filter(admin_dept=admin_department))

    context = {
        'institution': institution,
        'admin_dept': admin_department,
        'round': round,
        'project_type_fields': ['project_type_{}'.format(i) for i in range(1, number_of_types + 1)],
        'project_keyword_fields': ['project_keyword_{}'.format(i) for i in range(1, number_of_keywords + 1)]
    }

    if request.method == 'POST':
        form = StudentForm(request.POST, institution=institution, admin_department=admin_department, round=round)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            email = form.cleaned_data['email']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            programme = form.cleaned_data['programme']
            project_types = ','.join([form.cleaned_data[field].name for field in context['project_type_fields']])
            project_keywords = ','.join([form.cleaned_data[field].name for field in context['project_keyword_fields']])
            prerequisites = ','.join(x.name for x in form.cleaned_data['prerequisites'])


            student = Student(
                student_id=student_number,
                email=email,
                last_name=last_name,
                first_name=first_name,
                programme=programme,
                project_types=project_types,
                project_keywords=project_keywords,
                prerequisites=prerequisites,
                admin_dept = admin_department,
                institution = institution,
                allocation_round = round
            )

            try:
                student.save()
                context['student'] = student
                return render(request, 'projects/students.html', context)
            except IntegrityError:
                form.add_error(None, 'Student with this student number already exists.')
                context['form'] = form
                context['errors'] = form.errors['__all__']
                return render(request, 'projects/students.html', context)
            
        else:
            print(form.errors)
            context["form"] = form
            context["errors"] = form.errors
            return render(request, 'projects/students.html', context)
    form = StudentForm(institution=institution, admin_department=admin_department, round=round)
    context['form'] = form

    return render(request, 'projects/students.html', context)
