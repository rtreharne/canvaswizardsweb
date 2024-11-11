from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
import datetime
import random
from .forms import ContactForm

from .forms import RegistrationForm
from .models import Event, Registration, Resource, Portfolio, VideoBackground, Tool
import random

def promo(request, event_id):

    event = Event.objects.get(id=event_id)
    context = {"event": event}

    return render(request, 'front/promo.html', context)

def index(request):

    context = {}

    events = Event.objects.all().order_by('date')
    portfolios = Portfolio.objects.filter(tool=False, visible=True).order_by('-datetime')
    tools = Tool.objects.filter(visible=True)

    # Only get events in the future
    events = [event for event in events if event.date >= datetime.date.today()]

    context["events"] = events
    context["portfolios"] = portfolios
    context["tools"] = tools

    backgrounds = VideoBackground.objects.all()

    if backgrounds:
        background = random.choice(backgrounds)
    else:
        background = None

    print("BACKGROUND", background.file.url)

    context["background"] = background

    # Update any events in progress
    for event in events:
        start = datetime.datetime.combine(event.date, event.time)

        finish = start + datetime.timedelta(hours=event.duration)
        if start <= datetime.datetime.now() <= finish:
            event.in_progress = True
            event.save()
        else:
            event.in_progress = False
            event.save()

    # Get past events
    past_events = [event for event in Event.objects.all().order_by('-date') if datetime.datetime.combine(event.date, event.time) < datetime.datetime.now()]
    context["past_events"] = past_events

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            context["thanks"] = "Thank you for your message! I will get back to you shortly."
        else:
            context["contact_"] = contact_form
            return render(request, 'front/index.html', context)
        
    contact_form = ContactForm()
    context["contact_form"] = contact_form

    return render(request, 'front/index.html', context)

def register(request, event_id):

    event = Event.objects.get(id=event_id)
    resources = Resource.objects.filter(events=event)


    context = {"event": event}
    context["resources"] =  resources

    # If event is in the past, redirect to index
    if event.date < datetime.datetime.now().date():
        return render(request, 'front/event.html', context)


    if request.method == 'POST':

        registration_form = RegistrationForm(request.POST, event=event)
        if registration_form.is_valid():
            registration = registration_form.save()

            # Get event from form
            event = registration_form.cleaned_data['event']
            mode = registration_form.cleaned_data['mode']

            if mode == "Online":
                event.registrations_online += 1
            else:
                event.registrations += 1

            event.save()

            # Get first name from form
            first_name = registration_form.cleaned_data['first_name']
            context["thanks"] = f"Thank you {first_name}!"
            context["registration"] = registration
            context["event"] = event
            return render(request, 'front/event.html', context)
        else:

            context["form"] = registration_form
            return render(request, 'front/event.html', context)
    
    context["form"] = RegistrationForm(event=event)

    # Create a verbose name of "Where are you from?" for organization field
    context["form"].fields['organization'].label = "Where are you from?"

    # Create help text for organization field
    context["form"].fields['organization'].help_text = "(Organization, School, Department etc.)"

    # Create a verbose name of "Suggest a track for the playlist" for track field
    context["form"].fields['track'].label = "Suggest a track for the event playlist"

    robot_tracks = [
        '"Robots Have Feelings Too", by Crackout',
        '"Robot" by The Futureheads',
        '"Robot Rock" by Daft Punk',
        '"Robot" by Tatu',
        '"Robot" by Tripod',
        '"Robot" by The Dandy Warhols',
        '"Killer Robots From Venus" by The Arrogant Worms',
        '"Robot Boy" by Linkin Park',
        '"The Cyborg Slayers" by Dethklok',
        '"Robot Factory" by Jimmy Eat World',
        '"Paranoid Android" by Radiohead',
        '"Robot Parade" by They Might Be Giants',
        '"The Humans Are Dead" by Flight of the Conchords',
        '"Yoshimi Battles the Pink Robots" by Flaming Lips',
        '"Robophobia" by Electric President',
        '"Robot" by Miley Cyrus',
        '"None of Them Knew They Were Robots" by Mr. Bungle']

    # Create help text for track field
    track = random.choice(robot_tracks)
    context["form"].fields['track'].help_text = f"(e.g. {track})"

    # Get recommended tracks from registrations
    recommended_tracks = []
    for registration in Registration.objects.filter(event=event):
        if registration.track:
            recommended_tracks.append(registration.track + f" (Suggested by {registration.first_name})")
    if len(recommended_tracks) > 0:
        context["tracks"] = recommended_tracks
    
    
    return render(request, 'front/event.html', context)

def portfolio(request, portfolio_id):
        
        portfolio = Portfolio.objects.get(id=portfolio_id)

        if not portfolio.visible:
            return render(request, 'front/index.html')
    
        context = {"portfolio": portfolio}
    
        return render(request, 'front/portfolio.html', context)
