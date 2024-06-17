from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
from django.templatetags.static import static
from django.utils.safestring import mark_safe


class EnrollmentsForm(forms.Form):
    canvas_url = forms.URLField(label='Canvas URL')
    canvas_token = forms.CharField(label='Canvas Token', help_text="You can generate a Canvas Token by following the instructions <a href='https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89' target='_blank'>here</a>.")
    file = forms.FileField(
        label="File",
        help_text=mark_safe(
            "Upload an .xlsx file containing the enrollment information. "
            "Make sure your file matches the <a href='{}' download>enrollment template</a>."
            .format(static('template_files/enrollments_template.xlsx'))
        )
    )
    action = forms.ChoiceField(label='Action', choices=[('add', 'Add enrollments'), ('delete', 'Delete enrollments')], initial='add')
    notify = forms.BooleanField(label='Notify users', initial=True)
    # Make sure file is a .tsv file

    def clean_file(self):
        file = self.cleaned_data['file']

        if not file.name.endswith('.xlsx'):
            raise ValidationError('Please upload a .xlsx file.')

        # Can you read the first line of the file and check the headers?
        # If the headers are not as expected, raise a ValidationError.
        # The headers should be 'video_url', 'date', 'time', 'transcript_url', 'video_timestamp', 'transcript_text', 'transcript_timestamp'

        # Read the first line of the file
        df = pd.read_excel(file)
        # Split the first line into headers 
        headers = df.columns.tolist()
        # Check if the headers are as expected
        expected_headers = ['course_code', 'user_id', 'enrollment_type']
        if len(headers) != len(expected_headers):
            raise ValidationError('The headers in the file are not as expected.')
        
        # Check if the headers are in the expected order
        if set(headers) != set(expected_headers):
            raise ValidationError('The headers in the file are not as expected.')

        
        # check file size < 50 MB
        if file.size > 5 * 1024 * 1024:
            raise ValidationError('File size must be under 5 MB.')
        
        # Check file is not empty
        if not file.size:
            raise ValidationError('File is empty.')
        
        # Reset the file pointer to the beginning of the file
        file.seek(0)

        return file
    

    # Create an "agree to terms and conditions" checkbox.
    # This is a required field, so it must be checked.
    # Hyperlink the "terms and conditions" text to the URL of your terms and conditions.
    terms_and_conditions = forms.BooleanField(label='I agree to the <a href="#toc">terms and conditions</a>.')