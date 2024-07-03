from django.shortcuts import render, redirect
from .forms import DataSpellForm, DataSpellSample, DataSpellPin
from .models import Data
import pandas as pd
import numpy as np
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone



# Create your views here.
def index(request):

    context = {}

    if request.method == 'POST':
        form = DataSpellForm(request.POST, request.FILES)


        if form.is_valid():
            
            file = form.cleaned_data['file']
            label = form.cleaned_data['label']
            open_at = form.cleaned_data['open_at']
            close_at = form.cleaned_data['close_at']
            pin = form.cleaned_data['pin']
            sample_size = form.cleaned_data['sample_size']

            print("open_at", open_at)
            print("close_at", close_at)

            data = Data(
                label=label,
                open_at=open_at,
                close_at=close_at,
                pin=pin,
                sample_size=sample_size,
                file=file
            )
            data.save()

            domain = request.get_host()

            success = f"""Data Spell created!<br><br>
            
            Share this link with your students:<br><a href='https://{domain}/dataspell/{label}'>https://{domain}/dataspell/{label}</a><br><br>
            
            You can edit your Data Spell at:<br><a href='https://{domain}/dataspell/{label}/admin'>https://{domain}/dataspell/{label}/admin</a>"""


            context["success"] = success
        else:
            context["form"] = form
            context["error"] = "Invalid form."
            return render(request, 'sample/index.html', context)



    form = DataSpellForm()
    context["form"] = form
        

    return render(request, 'sample/index.html', context)

def admin(request, name):

    try:
        data_obj = Data.objects.get(label=name)
    except:
        return redirect('/')

    context = {}
    context["obj"] = data_obj

    if request.method == "POST":

        if "label" in request.POST:
            form = DataSpellForm(request.POST, request.FILES, instance=data_obj)
            print(request.POST)
            
            if form.is_valid():
                # I don't want to save a new model record. I want to update the data_obj instance with my form data
                form.save()
                messages.success(request, 'Data Spell updated!')
                return redirect(reverse('sample:admin', args=[form.instance.label]))
            else:
                context["error"] = "Invalid form."
                #print form errors
                print(form.errors.as_data())
            context["form"] = form
            return render(request, 'sample/admin.html', context)
            

        if "pin" in request.POST:

            print("HERE!", request.POST["pin"], data_obj.pin)

            if int(request.POST["pin"]) == data_obj.pin:
                form = DataSpellForm(instance=data_obj, file_path=data_obj.file.url)
            else:
                form = DataSpellPin()
                error = "Invalid Pin"
                context["error"] = error
                context["message"] = 'Update your Data Spell below. Don\'t forget to click Save.'
            context["form"] = form
            return render(request, 'sample/admin.html', context)

    form = DataSpellPin()
    guidance = "Need to update your Data Spell? Enter your 4-digit pin below to change your data or open/close dates."
    context["form"] = form
    context["guidance"] = guidance
    

    return render(request, 'sample/admin.html', context)


def sample(request, name):

    try:
        data_obj = Data.objects.get(label=name)
    except:
        return redirect('/')

    context = {}
    context["obj"] = data_obj

    if request.method == "POST":

        form = DataSpellSample(request.POST)

        if form.is_valid():
            # Get data and read it with pandas

            df = pd.read_csv(data_obj.file)

            unique_id = form.cleaned_data["unique_id"]

            np.random.seed(unique_id)

            sample_size = data_obj.sample_size

            if len(df) > sample_size:
                df = df.sample(n=data_obj.sample_size)

            # Create a HttpResponse object with the csv data
            response = HttpResponse(content_type='text/csv')

            fname = f"{data_obj.label}_{unique_id}.csv"
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(fname)

            # Write the DataFrame to the response
            df.to_csv(path_or_buf=response, index=False)
            
            
            return response

        else:
            context["form"] = form
            return render(request, "sample/sample.html", context)

    # if now is < data_obj.close_at and > data_obj.open_at
    now = timezone.now()
    
    if data_obj.open_at < now < data_obj.close_at:
        form = DataSpellSample()
        context["form"] = form
    else:
        error = "This Data Spell is not currently available."
        context["error"] = error

    return render(request, 'sample/sample.html', context)

def dataspell(request, name, unique_id):

    try:
        data_obj = Data.objects.get(label=name)
    except:
        return redirect('/')
    
    try:
        df = pd.read_csv(data_obj.file)

        np.random.seed(unique_id)

        sample_size = data_obj.sample_size
        
        if len(df) > sample_size:
            df = df.sample(n=data_obj.sample_size)

        response = HttpResponse(content_type='text/csv')

        fname = f"{data_obj.label}_{unique_id}.csv"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(fname)

        # Write the DataFrame to the response
        df.to_csv(path_or_buf=response, index=False)

        return response
    except Exception as e:
        # Handle exceptions or errors
        return HttpResponse(f"Error generating file: {str(e)}", status=500)
