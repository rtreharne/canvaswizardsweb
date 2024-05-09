from django.shortcuts import render
from projects.forms import SupervisorForm
from projects.models import Department, Institution, Supervisor, Institution
from .models import LearningObjective, Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponseNotFound

from django.shortcuts import render, redirect

from projects.models import Supervisor
from ilo.forms import CatalogueForm

# Create your views here.
def index(request):

    institution_slug = "liverpool"
    admin_department_slug = "sobs"

    admin_department = Department.objects.get(slug=admin_department_slug)

    if request.method == 'POST':
        form = SupervisorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower().replace(' ', '')
            department = form.cleaned_data['department']

            department = Department.objects.get(pk=department.id)
            # Look for the supervisor in the supervisors table
            # If they don't exist, return error message
            if not Supervisor.objects.filter(username=username, admin_dept=admin_department).exists():
                return render(request, 'ilo/index.html', {'error': 'Staff member not found', 'form': SupervisorForm(), 'institution': Institution.objects.get(slug=institution_slug)})
            else:
                supervisor = Supervisor.objects.get(username=username, admin_dept__slug=admin_department_slug)

                if supervisor.department is None:
                    # set supervisor department to department.id
                    supervisor.department = Department.objects.get(pk=department.id)
                    supervisor.active = True
                    supervisor.save()
                elif supervisor.department != department:
                    return render(request, 'ilo/index.html', {'error': 'Staff member to a different department.', 'form': SupervisorForm(), 'institution': Institution.objects.get(slug=institution_slug)})
            # redirect to /ilo/<username>
            return redirect('ilo:catalogue', username=username)

    form = SupervisorForm()

    context = {
        'form': form,
        'institution': Institution.objects.get(slug=institution_slug),
        'admin_department': Department.objects.get(slug=admin_department_slug),
    }
    return render(request, 'ilo/index.html', context)

def catalogue(request, username):
    try:
        staff = Supervisor.objects.get(username=username)
        if staff.department is None:
            return redirect('ilo:index')
    except Supervisor.DoesNotExist:
        return redirect('ilo:index')
    
    institution = Institution.objects.get(slug = 'liverpool')

    responses = Response.objects.filter(staff=staff)
    response_los = [x.learning_objective for x in responses]

    form = CatalogueForm(staff_id = staff.id)

    los = LearningObjective.objects.filter(type="LO")
    modules = set([x.module for x in los])

    module_list = []
    for module in modules:
        module_list.append(
            {
                "los": [x for x in los if x.module == module],
                "name": f"{module.code} - {module.name}",
                "code": module.code
            }
        )

    context = {}
    context['form'] = form
    context['institution'] = institution
    context['modules'] = module_list
    context['staff'] = staff
    context['responses'] = responses
    context['response_los'] = response_los

    return render(request, 'ilo/catalogue_form.html', context)

@csrf_exempt
def create_update(request, username):
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        staff = Supervisor.objects.get(pk=staff_id)
        active = request.POST.get('active')
        if active == 'true':
            active = True
        else:
            active = False

        print("STAFF: ", staff)
        lo_id = request.POST.get('lo_id')
        lo = LearningObjective.objects.get(pk=lo_id)

        response = Response.objects.filter(staff=staff, learning_objective=lo)
        if response.exists():
            response = response.first()
        else:
            response = Response(learning_objective=lo)
            # update response with staff object

        response.staff = staff
        response.additional_info = request.POST.get('additional_info')
        response.active = active
        response.save()
        print("SAVING RESPONSE: ", response)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})