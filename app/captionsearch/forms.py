from django import forms
from django.core.exceptions import ValidationError

class CaptionSearchRequestForm(forms.Form):
    canvas_url = forms.URLField(label='Canvas URL')
    canvas_token = forms.CharField(label='Canvas Token', help_text="You can generate a Canvas Token by following the instructions <a href='https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89' target='_blank'>here</a>.")
    course_id = forms.IntegerField(label='Course ID')

    file = forms.FileField(label="Captions file", help_text='Upload a .tsv file containing the captions you wish to make searchable.')

    # Make sure file is a .tsv file
    def clean_file(self):
        file = self.cleaned_data['file']

        if not file.name.endswith('.tsv'):
            raise ValidationError('Please upload a .tsv file.')

        # Can you read the first line of the file and check the headers?
        # If the headers are not as expected, raise a ValidationError.
        # The headers should be 'video_url', 'date', 'time', 'transcript_url', 'video_timestamp', 'transcript_text', 'transcript_timestamp'

        # Read the first line of the file
        first_line = file.readline().decode('utf-8').strip()
        # Split the first line into headers 
        headers = first_line.split('\t')
        # Check if the headers are as expected
        expected_headers = ['video_url', 'date', 'time', 'transcript_url', 'video_timestamp', 'transcript_text', 'transcript_timestamp', 'title', 'owner']
        if len(headers) != len(expected_headers):
            raise ValidationError('The headers in the file are not as expected.')
        
        # Check if the headers are in the expected order
        if set(headers) != set(expected_headers):
            raise ValidationError('The headers in the file are not as expected.')

        
        # check file size < 50 MB
        if file.size > 50 * 1024 * 1024:
            raise ValidationError('File size must be under 50 MB.')
        
        # Check file is not empty
        if not file.size:
            raise ValidationError('File is empty.')
        return file
    

    # Create an "agree to terms and conditions" checkbox.
    # This is a required field, so it must be checked.
    # Hyperlink the "terms and conditions" text to the URL of your terms and conditions.
    terms_and_conditions = forms.BooleanField(label='I agree to the <a href="#toc">terms and conditions</a>.')


class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': ''}))