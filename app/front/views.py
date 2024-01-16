from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
import datetime

from .forms import Contactform, RegistrationForm
from .models import Contact, Service, Event

def index(request):

    context = {}
    
    events = Event.objects.all().order_by('date')

    # Only get events in the future
    events = [event for event in events if event.date >= datetime.date.today()]

    context["events"] = events

    return render(request, 'front/index.html', context)

def register(request, event_id):

    event = Event.objects.get(id=event_id)
    context = {"event": event}

    print("EVENT DATE: ", event.date)

    # If event is in the past, redirect to index
    if event.date < datetime.date.today():
        return redirect('front:index')
    
    print("GETTING FORM")

    if request.method == 'POST':
        print("POSTING FORM")
        registration_form = RegistrationForm(request.POST, event=event)
        if registration_form.is_valid():
            registration_form.save()

            # Get first name from form
            first_name = registration_form.cleaned_data['first_name']
            context["thanks"] = f"Thank you {first_name}!"
            return render(request, 'front/event.html', context)
        else:
            # print form errors
            print(registration_form.errors)
    
    context["form"] = RegistrationForm(event=event)

    # Create a verbose name of "Where are you from?" for organization field
    context["form"].fields['organization'].label = "Where are you from?"
    
    
    return render(request, 'front/event.html', context)
