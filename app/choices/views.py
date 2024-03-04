from django.shortcuts import render

from .models import *


def index(request):

    programmes = Programme.objects.filter(visible=True).order_by('title')
    context = {
        'programmes': programmes,
    }

    return render(request, 'choices/index.html', context)


def programme_page(request, slug, query=None):
    
    programme = Programme.objects.get(slug=slug)
    rules = programme.rules.filter(programme=programme).order_by('title')
    tribes = programme.tribes.filter(programme=programme).order_by('title')
    modules = programme.programmes.filter(in_programmes=programme).order_by('code')
    years = list(set([x.year for x in modules]))
    context = {}
    context["years"] = years
    context["programme"] = programme
    context["modules"] = modules
    context["query"] = query
    context["tribes"] = tribes
    context["rules"] = rules
    
    return render(request, 'choices/programme.html', context)

