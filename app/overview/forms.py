from django import forms
import datetime

class DateInput(forms.DateInput):
    input_type = 'date'

class OverviewRequestForm(forms.Form):
    canvas_url = forms.URLField(label='Canvas URL')
    canvas_token = forms.CharField(label='Canvas Token', help_text="You can generate a Canvas Token by following the instructions <a href='https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89' target='_blank'>here</a>.")
    from_date = forms.DateField(label='From Date', help_text="Look for assignments with deadlines after this date.", widget=DateInput)
    to_date = forms.DateField(label='To Date', help_text="Look for assignments with deadlines before this date.", widget=DateInput)
    # Create a text field for an encryption password.
    # This is not a required field, but it is recommended.
    # Include help text to explain the purpose of the field.
    # The password will be used to encrypt the report file before it is uploaded to the server and will be required to decrypt the file when it is downloaded.
    encryption_password = forms.CharField(label='Encryption Password', required=False, help_text='Recommended for added security.')

    # Create an "agree to terms and conditions" checkbox.
    # This is a required field, so it must be checked.
    # Hyperlink the "terms and conditions" text to the URL of your terms and conditions.
    terms_and_conditions = forms.BooleanField(label='I agree to the <a href="#toc">terms and conditions</a>.')

    # Error trapping for input_file:
    # Must be .xlsx
    # Must be less than 5MB


    # make all fields required except for the encryption password
    def __init__(self, *args, **kwargs):
        super(OverviewRequestForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'encryption_password':
                field.required = True
            else:
                field.required = False
        
        # make file field required
        self.fields['from_date'].required = True
        self.fields['to_date'].required = True

        # set default date on 'to_date' as today
        self.fields['to_date'].initial = datetime.date.today()

        # set default date on 'from_date' as today - 1 month
        self.fields['from_date'].initial = datetime.date.today() - datetime.timedelta(days=30)
        
