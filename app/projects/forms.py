from django import forms
import datetime
from django.core.exceptions import ValidationError
from collections import OrderedDict
from django.core.validators import MaxValueValidator, MinValueValidator

from.models import Institute, Department, Institution, Admin, SupervisorSet, ProjectType, ProjectKeyword

def validate_min_keywords(value):
    if len(value) < 3:
        raise ValidationError('Please select at least 3 keywords.')

class SupervisorSetForm(forms.ModelForm):
    class Meta:
        model = SupervisorSet
        fields = '__all__'


    available_for_ug = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)], initial=3)
    available_for_pg = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)], initial=1)

    type = forms.ModelChoiceField(queryset=ProjectType.objects.all(), label='Type', help_text='Select the type of project you are offering.', required=True)
    keywords = forms.ModelMultipleChoiceField(
        queryset=ProjectKeyword.objects.all().order_by('name'), 
        label='Keywords',
        validators = [validate_min_keywords],
        help_text='Select a minimum of 3 keywords that best describe your project. Hold down Ctrl (CMD on Mac) to select multiple keywords.', 
        required=True)
    
    # Hide supervisor, institution and admin_dept fields
    def __init__(self, *args, **kwargs):
        super(SupervisorSetForm, self).__init__(*args, **kwargs)
        self.fields['supervisor'].widget = forms.HiddenInput()
        self.fields['institution'].widget = forms.HiddenInput()
        self.fields['admin_dept'].widget = forms.HiddenInput()
        self.fields['active'].widget = forms.HiddenInput()

        new_order = ['supervisor', 'institution', 'admin_dept', 'type', 'keywords', 'available_for_ug', 'available_for_pg', 'active']
        self.fields = OrderedDict((key, self.fields[key]) for key in new_order)

class InstitutionForm(forms.Form):
    user_type = forms.ChoiceField(choices=[('student', 'Student'), ('supervisor', 'Supervisor')], label='User Type', help_text='Select whether you are a student or supervisor.')
    institution_name = forms.ModelChoiceField(queryset=Institution.objects.all(), label='Institution')
    admin_department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Admin School/Department', help_text='This will be the school/department responsible for allocating the projects.')
    
    # create a field for choice of 'student' or 'staff'

    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)
        self.fields['admin_department'].widget.attrs['class'] = 'hidden'


class AdminDepartmentForm(forms.Form):
    name = forms.CharField(label='School/Department', help_text="Select the school/department responsible for your project allocation.")

    # get the institution from form kwargs
    def __init__(self, *args, **kwargs):
        institution_slug = kwargs.pop('institution_slug')
        super(AdminDepartmentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.Select()

        # Get all admins associated with institution_slug
        admin_departments = set([x.department for x in Admin.objects.filter(institution=institution_slug)])

        # Build a queryset of departments that are in admin_departments
        self.fields['name'].queryset = Department.objects.filter(id__in=[x.id for x in admin_departments])

       

class SupervisorForm(forms.Form):
    username = forms.CharField(label='MWS Username', help_text='This must be your managed Windows username')
    institute = forms.ModelChoiceField(queryset=Institute.objects.all(), label='Institute')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Department')

    # I want department to remain hidden initially.
    # Then I want to populate it with departments from the selected institute.

    def __init__(self, *args, **kwargs):
        super(SupervisorForm, self).__init__(*args, **kwargs)


        #self.fields['department'].widget = forms.HiddenInput()
        #self.fields['department'].queryset = Department.objects.none()

        # Set the CSS class for the department field to 'hidden'
        self.fields['department'].widget.attrs['class'] = 'hidden'
