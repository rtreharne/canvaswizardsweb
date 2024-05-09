from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'ilo'

urlpatterns = [
    path('', views.index, name='index'),
    path('create-update/<str:username>/', views.create_update, name='create-update'),
    path('<str:username>/', views.catalogue, name='catalogue'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
