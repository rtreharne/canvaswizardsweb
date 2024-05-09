from django import forms
from django.core.exceptions import ValidationError
from collections import OrderedDict
from django.forms.widgets import HiddenInput

class CatalogueForm(forms.Form):

    staff_id = forms.IntegerField(label="Staff ID", help_text="Enter your staff ID.")

    def __init__(self, *args, **kwargs):
        self.staff_id = kwargs.pop('staff_id', None)
        super(CatalogueForm, self).__init__(*args, **kwargs)
        self.fields['staff_id'].widget = HiddenInput()
        self.fields['staff_id'].initial = self.staff_id

