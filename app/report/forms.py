from django import forms

class ReportRequestForm(forms.Form):
    canvas_url = forms.URLField(label='Canvas URL')
    canvas_token = forms.CharField(label='Canvas Token')
    course_id = forms.IntegerField(label='Course ID')
    assignment_id = forms.IntegerField(label='Assignment ID')

    # make all fields required
    def __init__(self, *args, **kwargs):
        super(ReportRequestForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True
