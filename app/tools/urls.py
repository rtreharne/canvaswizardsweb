from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'tools'

urlpatterns = [
    path('enrollments/', views.enrollments, name='enrollments'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)