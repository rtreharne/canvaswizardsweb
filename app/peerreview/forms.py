from django import forms

class ReportRequestForm(forms.Form):
    canvas_url = forms.URLField(label='Canvas URL')
    canvas_token = forms.CharField(label='Canvas Token', help_text="You can generate a Canvas Token by following the instructions <a href='https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89' target='_blank'>here</a>.")
    course_id = forms.IntegerField(label='Course ID')
    assignment_id = forms.IntegerField(label='Assignment ID')

    # Create a text field for an encryption password.
    # This is not a required field, but it is recommended.
    # Include help text to explain the purpose of the field.
    # The password will be used to encrypt the report file before it is uploaded to the server and will be required to decrypt the file when it is downloaded.
    encryption_password = forms.CharField(label='Encryption Password', required=False, help_text='Recommended for added security.')

    # Create an "agree to terms and conditions" checkbox.
    # This is a required field, so it must be checked.
    # Hyperlink the "terms and conditions" text to the URL of your terms and conditions.
    terms_and_conditions = forms.BooleanField(label='I agree to the <a href="#toc">terms and conditions</a>.')
   


    # make all fields required except for the encryption password
    def __init__(self, *args, **kwargs):
        super(ReportRequestForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'encryption_password':
                field.required = True
            else:
                field.required = False
        
