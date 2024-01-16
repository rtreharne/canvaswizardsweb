from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper

from .models import Human

class HumanForm(forms.ModelForm):
    
    class Meta:
        model = Human
        fields = ['first_name', 'last_name']

    def save(self, commit=True):
        instance = super().save(commit=False)
        slug_base = slugify(f"{instance.first_name}-{instance.last_name}")
        unique_slug = slug_base[:20]  # Limit slug to 20 characters
        num = 1

        while Human.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug_base[:17]}-{num}"  # Limit slug to 17 characters and append num
            num += 1

        instance.slug = unique_slug

        if commit:
            instance.save()
        return instance

class IntegerInputForm(forms.Form):
    number = forms.IntegerField(label='Answer')

