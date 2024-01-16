from django import forms

from .models import Contact, Registration, Event

class Contactform(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'

class RegistrationForm(forms.ModelForm):

    # Get event_id from URL
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['event'].initial = event

    # Do not show events field
    event = forms.ModelChoiceField(queryset=Event.objects.all(), widget=forms.HiddenInput())
    
    class Meta:
        model = Registration
        fields = '__all__'
        