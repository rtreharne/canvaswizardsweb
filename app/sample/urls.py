from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'sample'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:instance_id>/', views.index, name='update_index'),
    path('<str:name>/', views.sample, name='sample'),
    path('<str:name>/admin', views.admin, name='admin')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)