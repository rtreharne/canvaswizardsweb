from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from .models import Data

class DataSpellPin(forms.Form):
    pin = forms.IntegerField(min_value=1000, max_value=9999, help_text='Enter the 4-digit PIN to access the data set.')

class DataSpellSample(forms.Form):

    unique_id = forms.IntegerField(min_value=100000000, max_value=999999999)

    terms_and_conditions = forms.BooleanField(label='I agree to the <a href="#toc">terms and conditions</a>.')


class DataSpellForm(forms.ModelForm):
    
    class Meta:
        model = Data
        fields = ['label', 'open_at', 'close_at', 'file', 'sample_size', 'pin']

    label = forms.CharField(max_length=128, help_text='Enter a label for the data set. Don\'t include spaces or special characters.')

    file = forms.FileField(
        label="File",
        help_text=mark_safe(
            "Upload an .csv file containing your full data set."
        )
    )
    
    sample_size = forms.IntegerField(
        label='Sample Size',
        help_text='Enter the number of rows you would like to sample from the data set.',
        min_value=1
    )

    open_at = forms.DateTimeField(
        label='Open At',
        help_text='Enter the date and time when the data set will be available.',
        widget=forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
        required=True
    )

    close_at = forms.DateTimeField(
        label='Close At',
        help_text='Enter the date and time when the data set will be available.',
        widget=forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
        required=True
    )

    pin = forms.IntegerField(min_value=1000, max_value=9999, help_text='Enter a 4-digit PIN to secure the data set.')

    def clean_label(self):
        label = self.cleaned_data['label']

        if ' ' in label:
            raise ValidationError('Label cannot contain spaces.')

        if not label.isalnum():
            raise ValidationError('Label can only contain alphanumeric characters.')

        return label

    def clean_file(self):
        file = self.cleaned_data['file']
    
        if not file.name.endswith('.csv'):
            raise ValidationError('Please upload a .csv file.')
        
        # check file size < 5 MB
        if file.size > 5 * 1024 * 1024:
            raise ValidationError('File size must be under 5 MB.')
        
        # Check file is not empty
        if not file.size:
            raise ValidationError('File is empty.')
        
        # Reset the file pointer to the beginning of the file
        file.seek(0)
    
        return file
    
    def __init__(self, *args, **kwargs):
        file_path = kwargs.pop('file_path', None)
        super(DataSpellForm, self).__init__(*args, **kwargs)
        if file_path:
            self.fields['file'].required = False
    
    # Create an "agree to terms and conditions" checkbox.
    # This is a required field, so it must be checked.
    # Hyperlink the "terms and conditions" text to the URL of your terms and conditions.
    terms_and_conditions = forms.BooleanField(label='I agree to the <a href="#toc">terms and conditions</a>.')