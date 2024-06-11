from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'captionsearch'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:course_name>/', views.course, name='course'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)