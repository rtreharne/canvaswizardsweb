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

    # Check uniqueness of email and event together
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        event = cleaned_data.get("event")
        if Registration.objects.filter(email=email, event=event).exists():
            raise forms.ValidationError(
                "You have already registered for this event. Nice one!"
            )
    
    class Meta:
        model = Registration
        fields = '__all__'
        