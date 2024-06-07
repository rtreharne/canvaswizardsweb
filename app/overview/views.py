from django.shortcuts import render
from .forms import OverviewRequestForm
from canvasapi import Canvas
from .models import OverviewProfile, OverviewRequest
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .utils import overview_report
import datetime
from .tasks import generate_report



def download_and_delete_file(request, report_request_id):

    report_request = OverviewRequest.objects.get(id=report_request_id)

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
    old_requests = OverviewRequest.objects.filter(created__lt=timezone.now() - timedelta(hours=24))
    for request in old_requests:
        request.file.delete()
        request.delete()

    
    return OverviewRequest.objects.filter(profile=request_user).order_by('-created')


def index(request, uuid=None):

    context = {}

    if request.method == 'POST':
        form = OverviewRequestForm(request.POST, request.FILES)
        print("Got a POST request")
        if form.is_valid():
            print("Form is valid")
            CANVAS_TOKEN = form.cleaned_data['canvas_token']
            CANVAS_URL = form.cleaned_data['canvas_url']
            encryption_password = form.cleaned_data['encryption_password']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']

            try:
                canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
                print('Connected to Canvas')
                print(CANVAS_TOKEN)
                print(CANVAS_URL)
            except:
                # Add form error
                return render(request, 'Overview/index.html', {'form': form, 'error': 'Could not connect to Canvas. Invalid token or URL.'})

            try:
                user_id = canvas.get_current_user().id
                user = canvas.get_user(user_id)
                profile = user.get_profile()
            except:
                return render(request, 'Overview/index.html', {'form': form, 'error': 'Could not find user. Invalid token or URL.'})

            email = profile['primary_email']
            name = profile['sortable_name']
            short_name = profile['short_name']
            bio = profile['bio']

            # Get or create a ReportProfile object
            profile_obj, created = OverviewProfile.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'short_name': short_name,
                    'bio': bio,
                },
            )

            uuid = profile_obj.uuid

            try:
                # Create a ReportRequest object
                report_request = OverviewRequest(profile=profile_obj)
                report_request.from_date = from_date
                report_request.to_date = to_date
                report_request.save()
            except:
                return render(request, 'overview/index.html', {'form': form, 'error': 'Could not find course or assignment. Check course and assignment ID.'})
            
            generate_report.delay(CANVAS_URL, CANVAS_TOKEN, report_request.id, from_date, to_date, encryption_password=encryption_password)

            return HttpResponseRedirect(reverse('overview:index-uuid', args=[uuid]))
        
        else:
            # get the errors
            print("Form is not valid")
            print(form.errors)


    if uuid:
        try:
            profile = OverviewProfile.objects.get(uuid=uuid)

            requests = delete_old_requests(profile)
                    
            context['profile'] = profile
            context['requests'] = requests


        except:
            pass

    context['form'] = OverviewRequestForm()

    return render(request, 'overview/index.html', context)
