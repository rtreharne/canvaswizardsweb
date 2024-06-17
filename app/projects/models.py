from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

class Institution(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    logo = models.ImageField(upload_to='institute_logos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug = slugify(self.name)
            while Institution.objects.filter(slug=self.slug).exists():
                self.slug = '{}-{}'.format(slug, get_random_string(4))
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    
class Institute(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug = slugify(self.name)
            while Institute.objects.filter(slug=self.slug, institution=self.institution).exists():
                self.slug = '{}-{}'.format(slug, get_random_string(4))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Department(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, null=True, blank=True)
    help_video_iframe = models.CharField(max_length=10000, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug = slugify(self.name)
            while Department.objects.filter(slug=self.slug, institute=self.institute).exists():
                self.slug = '{}-{}'.format(slug, get_random_string(4))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Programme(models.Model):
    name = models.CharField(max_length=255)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programme_admin_dept', null=True, blank=True)
    ug_or_pg = models.CharField(max_length=2, choices=[('UG', 'UG'), ('PG', 'PG')], default='UG', verbose_name='UG/PG')


    def __str__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=255)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='location_admin_dept', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Round(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    number_of_types = models.IntegerField(default=3)
    number_of_keywords = models.IntegerField(default=3)

    start_date = models.DateField()
    end_date = models.DateField()
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='round_admin_dept', null=True, blank=True)

    # Add constraint. Name is unique for institution and admin_dept
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'institution', 'department'], name='unique_round')
        ]

    def __str__(self):
        return self.name
    
class Student(models.Model):
    student_id = models.IntegerField()
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    mbiolsci = models.BooleanField(default=False)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True)
    allocation_round = models.ForeignKey(Round, on_delete=models.CASCADE, null=True, blank=True)

    project_types = models.CharField(max_length=1000, null=True, blank=True)
    project_keywords = models.CharField(max_length=1000, null=True, blank=True)

    priority = models.CharField(max_length=1000, null=True, blank=True)

    prerequisites = models.CharField(max_length=1000, null=True, blank=True)

    mbiolsci = models.CharField(max_length=128, null=True, blank=True)

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_id', 'allocation_round'], name='unique_student_round')
        ]
    
    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
    
class Prerequisite(models.Model):
    name = models.CharField(max_length=20)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='prerequisite_admin_dept', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'institution'], name='unique_prerequisite')
        ]

    def __str__(self):
        return self.name
    
class Supervisor(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='upervisor_admin_dept', null=True, blank=True)
    active = models.BooleanField(default=False)
    projects_UG = models.IntegerField(default=3)
    projects_PG = models.IntegerField(default=1)
    max_projects = models.IntegerField(default=4)

    # ensure that when saving username is all lowercase with no spaces or special characters
    def save(self, *args, **kwargs):
        self.username = self.username.lower().replace(' ', '')
        super().save(*args, **kwargs)

    # ensure that username and institution are unique together
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username', 'admin_dept'], name='unique_supervisor')
        ]
        ordering = ['username']

    def __str__(self):
        return self.username
    
class SupervisorSet(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='supervisor_set_admin_dept', null=True, blank=True)

    keywords = models.ManyToManyField('ProjectKeyword', blank=True,  related_name='supervisor_set_keywords')
    type = models.ForeignKey('ProjectType', blank=True, null=True, on_delete=models.CASCADE, related_name='supervisor_set_types')
    prerequisite = models.ForeignKey('Prerequisite', blank=True, null=True, on_delete=models.CASCADE, related_name='supervisor_set_prerequisites')
    available_for_ug = models.PositiveIntegerField(default=3, verbose_name='Available for UG')
    available_for_pg = models.PositiveIntegerField(default=1, verbose_name='Available for PG')
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Check if the SupervisorSet instance is being created or updated

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            print("Creating new projects", self.available_for_ug)
            # Create n UG projects
            for _ in range(self.available_for_ug):
                print("Creating UG project")
                Project.objects.create(supervisor_set=self, ug_or_pg='UG')

            # Create m PG projects
            for _ in range(self.available_for_pg):
                Project.objects.create(supervisor_set=self, ug_or_pg='PG')

    def __str__(self):
        return self.supervisor.email
    
class Admin(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True)



    def __str__(self):
        return self.last_name
    
class ProjectType(models.Model):
    name = models.CharField(max_length=255)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='project_type_admin_dept', null=True, blank=True)

    limit_to_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='limit_to_department')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'admin_dept'], name='unique_project_type')
        ]

    def __str__(self):
        return self.name
    
class ProjectKeyword(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='project_keyword_admin_dept', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    exclude_programmes = models.ManyToManyField(Programme, blank=True, related_name='exclude_programmes')
    ug_only = models.BooleanField(default=False)
    pg_only = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'admin_dept'], name='unique_project_keyword')
        ]

    # Add constraint. Can't be both ug_only and pg_only
    def clean(self):
        if self.ug_only and self.pg_only:
            raise ValidationError('Project keyword cannot be both UG only and PG only')

    def __str__(self):
        return self.name

class Project(models.Model):
    supervisor_set = models.ForeignKey(SupervisorSet, on_delete=models.CASCADE)
    primary_supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='primary_supervisor')
    second_supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='second_supervisor')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, null=True, blank=True, related_name='round')
    active = models.BooleanField(default=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='student')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    admin_dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    
    # ug_or_pg
    ug_or_pg = models.CharField(max_length=2, choices=[('UG', 'UG'), ('PG', 'PG')], default='UG', verbose_name='UG/PG')
    
    def save(self, *args, **kwargs):
        self.primary_supervisor = self.supervisor_set.supervisor
        self.round = self.supervisor_set.institution.round_set.latest('start_date')
        self.institution = self.supervisor_set.institution
        self.admin_dept = self.supervisor_set.admin_dept
        super().save(*args, **kwargs)

    def __str__(self):
        return self.supervisor_set.supervisor.email

    

