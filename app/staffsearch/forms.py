from django import forms
from staffsearch.models import Department

departments = Department.objects.all().order_by('name')
try:
    department_list = [(x.name, x.name) for x in departments]
except:
    department_list = []

class SearchForm(forms.Form):
    CHOICES = [("All Departments", "All Departments"),
               ("------------", "------------")]
    CHOICES.extend(department_list)

    CHOICES = tuple(CHOICES)

    keyword = forms.CharField(label="Search", max_length=100,
                              widget=forms.TextInput(attrs={'placeholder': "Search by keyword or surname"}))
    department = forms.ChoiceField(choices=CHOICES)