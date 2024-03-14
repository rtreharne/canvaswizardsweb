from django.shortcuts import render
from .forms import ReportRequestForm
from canvasapi import Canvas
from .models import ReportRequest, ReportProfile
from .tasks import generate_report
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request, uuid=None):

    context = {}

   

    

    if request.method == 'POST':
        form = ReportRequestForm(request.POST)
        if form.is_valid():
            CANVAS_TOKEN = form.cleaned_data['canvas_token']
            CANVAS_URL = form.cleaned_data['canvas_url']
            course_id = form.cleaned_data['course_id']
            assignment_id = form.cleaned_data['assignment_id']

            try:
                canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
                print('Connected to Canvas')
            except:
                # Add form error
                return render(request, 'report/index.html', {'form': form, 'error': 'Could not connect to Canvas. Invalid token or URL.'})

            try:
                user_id = canvas.get_current_user().id
                user = canvas.get_user(user_id)
                profile = user.get_profile()
            except:
                return render(request, 'report/index.html', {'form': form, 'error': 'Could not find user. Invalid token or URL.'})

                
            
                
            email = profile['primary_email']
            name = profile['sortable_name']
            short_name = profile['short_name']
            bio = profile['bio']

            # Get or create a ReportProfile object
            profile_obj, created = ReportProfile.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'short_name': short_name,
                    'bio': bio,
                },
            )

            uuid = profile_obj.uuid

            # Create a ReportRequest object
            report_request = ReportRequest(profile=profile_obj)
            report_request.save()
            
            try:
                course = canvas.get_course(course_id)
                assignment = course.get_assignment(assignment_id)

                report_request.course_code = course.course_code
                report_request.assignment_name = assignment.name
                report_request.save()
            except:
                return render(request, 'report/index.html', {'form': form, 'error': 'Could not find course or assignment. Check course and assignment ID.'})
            
            generate_report.delay(CANVAS_URL, CANVAS_TOKEN, report_request.id, course_id, assignment_id)

            return HttpResponseRedirect(reverse('report:index-uuid', args=[uuid]))

    if uuid:
        try:
            profile = ReportProfile.objects.get(uuid=uuid)
            requests = ReportRequest.objects.filter(profile=profile).order_by('-created')
            context['profile'] = profile
            context['requests'] = requests
        except:
            pass

    context['form'] = ReportRequestForm()

    return render(request, 'report/index.html', context)
