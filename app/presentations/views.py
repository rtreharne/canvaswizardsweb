from django.shortcuts import render
from .forms import ShowcaseRequestForm
from canvasapi import Canvas
from .models import PresentationProfile, PresentationRequest
from .tasks import task_showcase

def showcase(request, uuid):
    try:
        report_request = PresentationRequest.objects.get(uuid=uuid)
    except:
        return render(request, 'presentations/showcase.html', {'error': 'Could not find showcase.'})
    context = {'report_request': report_request}
    
    return render(request, 'presentations/showcase.html', context)

def index(request):

    context = {}

    if request.method == 'POST':
        form = ShowcaseRequestForm(request.POST)
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
            profile_obj, created = PresentationProfile.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'short_name': short_name,
                    'bio': bio,
                },
            )

            try:
                course = canvas.get_course(course_id)
                assignment = course.get_assignment(assignment_id)

                # Create a ReportRequest object
                report_request = PresentationRequest(profile=profile_obj)

                report_request.course_code = course.course_code
                report_request.assignment_name = assignment.name[:100]
                report_request.save()
            except:
                print("Got a problem here")
                return render(request, 'report/index.html', {'form': form, 'error': 'Could not find course or assignment. Check course and assignment ID.'})
            
            domain = request.get_host()
            task_showcase.delay(CANVAS_URL, CANVAS_TOKEN, report_request.id, course_id, assignment_id, domain)

            success = "Showcase incantation performed successfully!<br><br> A new module containing your showcase page will appear in your Canvas course shortly at the following URL: <br><br><a href='{0}/courses/{1}/modules'>{0}/courses/{1}/modules</a><br><br>Make sure you publish the module and page!".format(CANVAS_URL, course_id)
            context['success'] = success
            form = ShowcaseRequestForm()
            context['form'] = form

            return render(request, 'presentations/index.html', context)

    form = ShowcaseRequestForm()
    context['form'] = form
    
    return render(request, 'presentations/index.html', context)
