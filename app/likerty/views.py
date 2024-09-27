from django.shortcuts import render
from .forms import SurveyForm, ResponseForm, ResponseLoopForm
from .models import Survey, Response
from django.shortcuts import redirect
from django.http import HttpResponseNotFound
import os
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

# from settings import BASE_URL
from django.conf import settings
from allauth.socialaccount.models import SocialApp

# import sites model







def index(request):

    SITE_ID = settings.SITE_ID


    # choose a random file from static/backgrounds
    backgrounds = os.listdir('likerty/static/backgrounds')
    background = random.choice(backgrounds)

    context = {}
    context["background"] = f"backgrounds/{background}"

    if request.user.is_authenticated:
        social_account = SocialAccount.objects.filter(user=request.user).first()
        context["social_account"] = social_account

    return render(request, 'likerty/index.html', context)

def share(request, slug):
    survey = Survey.objects.get(label=slug)
    context = {}
    context["survey"] = survey
    context["base_url"] = f"{request.scheme}://{request.get_host()}"
    print("base_url", context["base_url"])
    return render(request, 'likerty/share.html', context)

# If logged in user, else redirect to login
@login_required
def create(request):

    context = {}

    base_url = f"{request.scheme}://{request.get_host()}"

    if request.method == 'POST':
        form = SurveyForm(request.POST, request=request)
        if form.is_valid():
            survey = form.save()
            context["thanks"] = True
            context["survey"] = survey
            context["base_url"] = base_url
            return render(request, 'likerty/create.html', context)

        # else return the form with errors
        else:
            context = {}
            context["form"] = form
            return render(request, 'likerty/create.html', context)


    
    context["form"] = SurveyForm(request=request)
    return render(request, 'likerty/create.html', context)

@csrf_exempt
def response(request, slug):


    if request.path == '/favicon.ico/':
        return HttpResponseNotFound()

    context = {}

    print("slug", slug)

    try:
        survey = Survey.objects.get(label=slug)
    except Survey.DoesNotExist:
        return redirect('likerty:index')

    if request.method == 'POST':

        form = ResponseForm(request.POST, survey=survey)
        
        if form.is_valid():
            response = form.save()

            if survey.comments_on:
                context["survey"] = survey
                context["form"] = ResponseForm(instance=response, survey=survey)
                context["response"] = response

                # post the response to the chat
                return render(request, 'likerty/chat.html', context)
            else:
                context["thanks"] = True
                if survey.redirect_url:
                    return redirect(survey.redirect_url)
                else:
                    context["survey"] = survey
                    return render(request, 'likerty/response.html', context)
                    
    context["form"] = ResponseForm(survey=survey)
    context["survey"] = survey
                
    return render(request, 'likerty/response.html', context)
            

def response_loop(request, slug):

    survey = Survey.objects.get(label=slug)

    print("slug", slug)

    context = {}

    base_url = f"{request.scheme}://{request.get_host()}"

    if request.method == 'POST':
        form = ResponseLoopForm(request.POST, survey=survey)
        if form.is_valid():
            form.save()

    form = ResponseLoopForm(survey=survey)
    context["form"] = form
    context["survey"] = survey


    # choose a random file from static/backgrounds
    backgrounds = os.listdir('likerty/static/backgrounds')
    background = random.choice(backgrounds)
    context["background"] = f"backgrounds/{background}"
    context["base_url"] = base_url

    return render(request, 'likerty/response-loop.html', context)

def summary(request, slug):

    if request.path == '/favicon.ico/':
        return HttpResponseNotFound()
    
    survey = Survey.objects.get(label=slug)
    responses = Response.objects.filter(survey=survey).order_by('-created_at')
    context = {}
    context["survey"] = survey
    context["responses"] = responses

    context["fivestar"] = len([response for response in responses if response.response == 5])
    context["fourstar"] = len([response for response in responses if response.response == 4])
    context["threestar"] = len([response for response in responses if response.response == 3])
    context["twostar"] = len([response for response in responses if response.response == 2])
    context["onestar"] = len([response for response in responses if response.response == 1])

    max_rating = max(context["fivestar"], context["fourstar"], context["threestar"], context["twostar"], context["onestar"])

    try:
        context["fivestarwidth"] = round(context["fivestar"] / max_rating * 100)
        context["fourstarwidth"] = round(context["fourstar"] / max_rating * 100)
        context["threestarwidth"] = round(context["threestar"] / max_rating * 100)
        context["twostarwidth"] = round(context["twostar"] / max_rating * 100)
        context["onestarwidth"] = round(context["onestar"] / max_rating * 100)
    except ZeroDivisionError:
        context["fivestarwidth"] = 0
        context["fourstarwidth"] = 0
        context["threestarwidth"] = 0
        context["twostarwidth"] = 0
        context["onestarwidth"] = 0

    context["avg_rating"] = survey.response_set.aggregate(models.Avg('response'))['response__avg']
    context["response_count"] = survey.response_set.count()
    context["comment_count"] = survey.response_set.filter(comment__isnull=False).count()

    try:
        context["last_response_date"] = survey.response_set.order_by('-created_at').first().created_at
    except AttributeError:
        context["last_response_date"] = "No responses yet"


    return render(request, 'likerty/summary.html', context)


def chat(request, slug):

    survey = Survey.objects.get(slug=slug)

    context = {}
    context["survey"] = survey

    return render(request, 'likerty/chat.html', context)

@csrf_exempt
def update_comment(request):
    if request.method == 'POST':
       
        print("SUCCESS")

        response_id = int(request.POST['response_id'])

        response = Response.objects.get(pk=response_id)

        response.comment = request.POST['comment']

        response.save()

        # Return the updated comment as a JSON response
        return JsonResponse({'comment': 'Comment updated successfully'}, status=200)
        

    # If the request method is not POST, return a 405 Method Not Allowed response
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def logout_view(request):
    # Log out the user
    logout(request)

    # Get the next URL from the 'next' parameter, or default to the homepage
    next_url = request.GET.get('next', '/')

    # Redirect to the next URL
    return redirect(next_url)

@login_required
def dash(request):

    # Get user
    user = request.user

    # Get surveys created by user
    surveys = Survey.objects.filter(user=user)


    survey_set = [{
        "survey": survey,
        "avg_rating": survey.response_set.aggregate(models.Avg('response'))['response__avg'],
        "response_count": survey.response_set.count(),
        "comment_count": survey.response_set.filter(comment__isnull=False).count(),
        "last_response_date": 0,
    } for survey in surveys]


    context = {}
    context["surveys"] = survey_set
    context["user"] = user
    

    return render(request, 'likerty/dash.html', context)


@login_required
def edit(request, slug):

    survey = Survey.objects.get(label=slug)

    if request.method == 'POST':
        form = SurveyForm(request.POST, request=request, instance=survey)
        if form.is_valid():
            form.save()

            # If from summary
            if request.GET.get('summary'):
                return HttpResponseRedirect(reverse('likerty:summary', args=[survey.label]))

            return HttpResponseRedirect(reverse('likerty:dash') + f'#{survey.label}')
        else:
            form = SurveyForm(request=request, instance=survey)
            context = {}
            context["form"] = form
            context["survey"] = survey
            return render(request, 'likerty/create.html', context)

    form = SurveyForm(request=request, instance=survey)

    context = {}
    context["form"] = form
    context["survey"] = survey
    context["update"] = True

    if request.GET.get('dash'):
        context["dash"] = survey.label

    if request.GET.get('summary'):
        context["summary"] = True




    return render(request, 'likerty/create.html', context)

@require_POST
@csrf_exempt
def like_response(request):
    response_id = request.POST.get('response_id')
    response = Response.objects.get(id=response_id)
    response.likes += 1
    response.save()
    return JsonResponse({'number': response.likes})

@require_POST
@csrf_exempt
def dislike_response(request):
    response_id = request.POST.get('response_id')
    response = Response.objects.get(id=response_id)
    response.dislikes += 1
    response.save()
    return JsonResponse({'number': response.dislikes})

@require_POST
@csrf_exempt
def abuse_response(request):
    response_id = request.POST.get('response_id')
    response = Response.objects.get(id=response_id)
    response.abuse += 1
    response.save()
    return JsonResponse({'number': response.abuse})

@require_POST
@csrf_exempt
def hide_response(request):
    response_id = request.POST.get('response_id')
    response = Response.objects.get(id=response_id)
    response.hidden = True
    response.save()
    return JsonResponse({'hidden': "true"})

@require_POST
@csrf_exempt
def unhide_response(request):
    response_id = request.POST.get('response_id')
    response = Response.objects.get(id=response_id)
    response.hidden = False
    response.save()
    return JsonResponse({'unhidden': "true"})

@require_POST
@csrf_exempt
def delete_response(request):
    response_id = request.POST.get('response_id')
    response = get_object_or_404(Response, id=response_id)
    print("deleting response")
    response.delete()
    return JsonResponse({'status': 'success'})
