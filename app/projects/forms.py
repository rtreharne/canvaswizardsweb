from django import forms
import datetime
from django.core.exceptions import ValidationError
from collections import OrderedDict
from django.core.validators import MaxValueValidator, MinValueValidator


from.models import Institute, Department, Institution, Admin, SupervisorSet, ProjectType, ProjectKeyword, Prerequisite, Programme


class CsvImportForm(forms.Form):
    file = forms.FileField(label="File", help_text="Upload a .csv file containing the data you wish to import.")

    # make sure it's a csv file
    def clean_csv_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.csv'):
            raise ValidationError('Please upload a .csv file.')
        return file
     

def validate_min_keywords(value):
    if len(list(value)) < 1:
        raise ValidationError('Please select at least 1 keyword.')
    

class SupervisorSetForm(forms.ModelForm):
    class Meta:
        model = SupervisorSet
        fields = '__all__'

    available_for_ug = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], initial=0)
    available_for_pg = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], initial=0)

    


    type = forms.ModelChoiceField(queryset=ProjectType.objects.all().order_by('name'), label='Type', help_text='Select the type of project you are offering.', required=True)
    keywords = forms.ModelMultipleChoiceField(
        queryset=ProjectKeyword.objects.all().order_by('name'), 
        label='Keywords',
        validators = [validate_min_keywords],
        help_text='Select a minimum of 1 keyword that best describe your project. Hold down Ctrl (CMD on Mac) to select multiple keywords.', 
        required=True)
    
    #prerequisite = forms.ModelChoiceField(queryset=Prerequisite.objects.all(), label='Prerequisite', required=False)
    
    # Hide supervisor, institution and admin_dept fields
    def __init__(self, *args, **kwargs):
        self.admin_department = kwargs.pop('admin_department', None)
        super(SupervisorSetForm, self).__init__(*args, **kwargs)
        self.fields['supervisor'].widget = forms.HiddenInput()
        self.fields['institution'].widget = forms.HiddenInput()
        self.fields['admin_dept'].widget = forms.HiddenInput()
        self.fields['active'].widget = forms.HiddenInput()

        # Only allow positive integers for available_for_ug and available_for_pg
        self.fields['available_for_ug'].widget.attrs['min'] = 0
        self.fields['available_for_pg'].widget.attrs['min'] = 0

        self.fields['available_for_ug'].widget.attrs['max'] = 5
        self.fields['available_for_pg'].widget.attrs['max'] = 5

        new_order = ['supervisor', 'institution', 'admin_dept', 'type', 'keywords', 'prerequisite', 'available_for_ug', 'available_for_pg', 'active']
        self.fields = OrderedDict((key, self.fields[key]) for key in new_order)

        self.fields['type'].queryset = ProjectType.objects.filter(admin_dept=self.admin_department).order_by('name')
        self.fields['keywords'].queryset = ProjectKeyword.objects.filter(admin_dept=self.admin_department).order_by('name')


    # Make sure that sum of available_for_ug and available_for_pg is greater than 1
    def clean(self):
        cleaned_data = super(SupervisorSetForm, self).clean()
        available_for_ug = cleaned_data.get('available_for_ug')
        available_for_pg = cleaned_data.get('available_for_pg')

        if available_for_ug + available_for_pg < 1:
            raise ValidationError('The total number of projects available must be at least 1.')

        return cleaned_data


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
        admin_departments = set([x.department for x in Admin.objects.filter(institution=institution_slug)]).order_by('name')

        # Build a queryset of departments that are in admin_departments
        self.fields['name'].queryset = Department.objects.filter(id__in=[x.id for x in admin_departments]).order_by('name')

       

class SupervisorForm(forms.Form):
    username = forms.CharField(label='MWS Username', help_text='This must be your managed Windows username')
    institute = forms.ModelChoiceField(queryset=Institute.objects.all().order_by('name'), label='Institute')
    department = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'), label='Department')


    # I want department to remain hidden initially.
    # Then I want to populate it with departments from the selected institute.

    def __init__(self, *args, **kwargs):
        super(SupervisorForm, self).__init__(*args, **kwargs)


        #self.fields['department'].widget = forms.HiddenInput()
        #self.fields['department'].queryset = Department.objects.none()

        # Set the CSS class for the department field to 'hidden'
        self.fields['department'].widget.attrs['class'] = 'hidden'

        

class StudentForm(forms.Form):
    

    def clean_student_number(self):
        student_number = self.cleaned_data['student_number']
        if len(str(student_number)) != 9:
            raise ValidationError('Please enter a 9-digit student number.')
        return student_number
    
    def __init__(self, *args, **kwargs):
        self.institution = kwargs.pop('institution')
        self.department = kwargs.pop('admin_department')
        self.round = kwargs.pop('round')
    
        super(StudentForm, self).__init__(*args, **kwargs)

        if self.round.number_of_types < len(ProjectType.objects.filter(admin_dept=self.round.admin_dept)):
            number_of_types = self.round.number_of_types
        else:
            number_of_types = len(ProjectType.objects.filter(admin_dept=self.round.admin_dept))

        if self.round.number_of_keywords < len(ProjectKeyword.objects.filter(admin_dept=self.round.admin_dept)):
            number_of_keywords = self.round.number_of_keywords
        else:
            number_of_keywords = len(ProjectKeyword.objects.filter(admin_dept=self.round.admin_dept))



        for i in range(number_of_types):
            field_name = f'project_type_{i+1}'
            self.fields[field_name] = forms.ModelChoiceField(queryset=ProjectType.objects.filter(admin_dept=self.department).order_by('name'), label=f'Project type {i+1}')

        for i in range(number_of_keywords):
            field_name = f'project_keyword_{i+1}'
            self.fields[field_name] = forms.ModelChoiceField(queryset=ProjectKeyword.objects.filter(admin_dept=self.department).order_by('name'), label=f'Project topic {i+1}')

        self.fields['prerequisites'] = forms.ModelMultipleChoiceField(
            queryset=Prerequisite.objects.filter(admin_dept=self.department), 
            label='Prerequisites met', 
            help_text='Select a minimum of 5 modules that you have completed. Hold down Ctrl (CMD on Mac) to select multiple keywords.',
            required=True)
        
        self.fields['programme'] = forms.ModelChoiceField(queryset=Programme.objects.filter(admin_dept=self.department).order_by('name'), label='Programme/Pathway', help_text='Select your programme (or pathway if MBiolSci).')
        
    # create field student_number. Must be 9-digit integer
    student_number = forms.IntegerField(label='Student Number', help_text='Please enter your 9-digit student number.')
    last_name = forms.CharField(label='Last Name')
    first_name = forms.CharField(label='First Name')
    email = forms.EmailField(label='UoL Email Address')

    # create field for mbiolsci boolean with radio buttons for yes/no and no default
    mbiolsci = forms.ChoiceField(choices=[('', '---------'), ('yes', 'Yes'), ('no', 'No')], label='Are you a 4th year MBiolSci student?', required=True, initial=None)
    programme = forms.ModelChoiceField(queryset=Programme.objects.all(), label='Programme/Pathway', help_text='Select your programme (or pathway if MBiolSci).')

    # create a choice field to ask the question: "Allocation priority?" with options "Prioritise by project type", "Prioritise by topic", "No preference"
    allocation_priority = forms.ChoiceField(choices=[('type', 'Prioritise by project type'), ('topic', 'Prioritise by project topic'), ('none', 'No preference')], label='Allocation priority', help_text='Select your preference for project allocation.', initial='none')

    comment = forms.CharField(label='Comments', widget=forms.Textarea, help_text='Please provide any additional information that you think may be relevant to your project allocation.', required=False)

    # Make sure student selects at least 5 prerequisites
    def clean_prerequisites(self):
        prerequisites = self.cleaned_data['prerequisites']
        if len(Prerequisite.objects.filter(admin_dept=self.department)) >= 5:
            if len(list(prerequisites)) < 5:
                raise ValidationError('Please select at least 5 prerequisites.')
            return prerequisites
        else:
            return prerequisites






    
