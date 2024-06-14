from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='index'),
    #path('<str:institution_slug>/', views.admin_department, name='admin-department'),
    path('<str:institution_slug>/<str:admin_department_slug>/supervisor', views.supervisors, name='supervisor'),
    path('<str:institution_slug>/<str:admin_department_slug>/supervisor/<str:supervisor_username>', views.supervisor_dash, name='supervisor-dash'),
    path('<str:institution_slug>/<str:admin_department_slug>/student', views.students, name='students'),
    path('<str:institution_slug>/<str:admin_department_slug>/student/topics', views.topics, name='topics'),
    path('get-admin-departments/', views.GetAdminDepartmentsView.as_view(), name='get-admin-departments'),
    path('get-departments/', views.GetDepartmentsView.as_view(), name='get-departments'),
    path('get-keywords/', views.GetKeywordsView.as_view(), name='get-keywords'),

    path('supervisor_sets/<int:supervisor_set_id>', views.delete_supervisor_set, name='delete-supervisor-set'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)