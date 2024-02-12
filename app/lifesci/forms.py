from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper

from .models import Human


class HumanForm(forms.ModelForm):
    
    class Meta:
        model = Human
        fields = ['user', 'first_name', 'last_name', 'anonymous_user']

    # Add help text for anonymous user
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['anonymous_user'].help_text = "Check this box if you want to be anonymous."

        # Set user field using request.user
        self.fields['user'].initial = self.user

        # Hide User field
        self.fields['user'].widget = forms.HiddenInput()


    def save(self, commit=True):
        instance = super().save(commit=False)
        slug_base = slugify(f"{self.user.first_name}-{self.user.last_name}")
        unique_slug = slug_base[:20]  # Limit slug to 20 characters
        num = 1

        while Human.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug_base[:17]}-{num}"  # Limit slug to 17 characters and append num
            num += 1

        instance.slug = unique_slug
        #instance.user = self.initial['user']

        if commit:
            instance.save()
        return instance

class IntegerInputForm(forms.Form):
    number = forms.IntegerField(label='Answer')
    figure = forms.FileField(label='Figure')

