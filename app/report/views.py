from django.shortcuts import render
from .forms import ReportRequestForm
from canvasapi import Canvas
from .models import ReportRequest, ReportProfile
from .tasks import generate_report
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta



def download_and_delete_file(request, report_request_id):

    report_request = ReportRequest.objects.get(id=report_request_id)

    # Create a FileResponse to send the file
    response = FileResponse(report_request.file)

    # Remove the file from the object and delete the file from the filesystem
    report_request.downloaded = True
    report_request.save()

    profile = report_request.profile
    profile.downloads += 1
    profile.save()


    # return a HttpResponse

    return response


def delete_old_requests(request_user):
    # Delete requests older than 24 hrs
    old_requests = ReportRequest.objects.filter(created__lt=timezone.now() - timedelta(hours=24))
    for request in old_requests:
        request.file.delete()
        request.delete()

    """ # Delete downloaded requests

    downloaded_requests = ReportRequest.objects.filter(profile=request_user, downloaded=True)


    for request in downloaded_requests:
        request.file.delete()
        request.delete()
    """
    
    return ReportRequest.objects.filter(profile=request_user).order_by('-created')


def index(request, uuid=None):

    context = {}

    if request.method == 'POST':
        form = ReportRequestForm(request.POST)
        if form.is_valid():
            CANVAS_TOKEN = form.cleaned_data['canvas_token']
            CANVAS_URL = form.cleaned_data['canvas_url']
            course_id = form.cleaned_data['course_id']
            assignment_id = form.cleaned_data['assignment_id']
            encryption_password = form.cleaned_data['encryption_password']

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

            try:
                course = canvas.get_course(course_id)
                assignment = course.get_assignment(assignment_id)

                # Create a ReportRequest object
                report_request = ReportRequest(profile=profile_obj)

                report_request.course_code = course.course_code
                report_request.assignment_name = assignment.name
                report_request.save()
            except:
                return render(request, 'report/index.html', {'form': form, 'error': 'Could not find course or assignment. Check course and assignment ID.'})
            
            generate_report.delay(CANVAS_URL, CANVAS_TOKEN, report_request.id, course_id, assignment_id, encryption_password)

            return HttpResponseRedirect(reverse('report:index-uuid', args=[uuid]))

    if uuid:
        try:
            profile = ReportProfile.objects.get(uuid=uuid)

            requests = delete_old_requests(profile)
                    
            context['profile'] = profile
            context['requests'] = requests


        except:
            pass

    context['form'] = ReportRequestForm()

    return render(request, 'report/index.html', context)
