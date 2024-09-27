from django import forms

import datetime
from .models import Survey, Response

class DateInput(forms.DateInput):
    input_type = 'date'

LIKERT_CHOICES = [
    (1, 'Very poor'),
    (2, 'Poor'),
    (3, 'OK'),
    (4, 'Good'),
    (5, 'Very good'),
]

class SurveyForm(forms.ModelForm):

    
    class Meta:
        model = Survey
        fields = '__all__'

    # Hide slug field in form
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SurveyForm, self).__init__(*args, **kwargs)

        # set user field to logged in user
        self.fields['user'].initial = self.request.user
        self.fields['user'].widget = forms.HiddenInput()

        self.fields['start'] = forms.DateField(label='From', help_text="Survey will be available from this date. Leave blank to let it start today!", widget=DateInput, required=False)
        self.fields['end'] = forms.DateField(label='From', help_text="Survey will be available until this date. Leave blank to let it live forever!", widget=DateInput, required=False)

        # change Label of "Label" field to "Unique Label"
        self.fields['label'].label = 'Unique Label'
        self.fields['label'].help_text = 'This will be used in the URL of your survey. E.g. "bobsburgers" will be available at "wwww.likertysplit.com/bobsburgers" '

        # Change label of "Question" field to "Prompt"
        self.fields['question'].label = 'Prompt'
        self.fields['question'].help_text = 'E.g. "How would you rate our service?" '

        # Hide Redirect url field for now
        self.fields['redirect_url'].widget = forms.HiddenInput()

    # Clean label. Only allow "-" and alphanumeric characters
    def clean_label(self):
        label = self.cleaned_data['label']
        if not label.replace('-', '').isalnum():
            raise forms.ValidationError('Only alphanumeric characters and "-" are allowed')
        return label.lower()





class ResponseForm(forms.ModelForm):
        response = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect)
    
        class Meta:
            model = Response
            fields = '__all__'
    
        # Hide survey field in form
        def __init__(self, *args, **kwargs):
            self.survey = kwargs.pop('survey', None)
            super(ResponseForm, self).__init__(*args, **kwargs)
            self.fields['survey'].initial = self.survey
            self.fields['survey'].widget = forms.HiddenInput()

            # Hide response label
            self.fields['response'].label = ''

class ResponseLoopForm(forms.ModelForm):
    response = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect)
    
    class Meta:
        model = Response
        fields = ['survey', 'response']
    
    # Hide survey field in form
    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('survey', None)
        super(ResponseLoopForm, self).__init__(*args, **kwargs)
        self.fields['survey'].initial = self.survey
        self.fields['survey'].widget = forms.HiddenInput()

        # Hide response label
        self.fields['response'].label = ''

class FeedbackForm(forms.ModelForm):
     pass