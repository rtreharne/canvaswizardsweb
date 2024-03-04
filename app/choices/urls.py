from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'choices'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:slug>/<str:query>', views.programme_page, name='programme-page'),
    path('<str:slug>/', views.programme_page, name='programme-page'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)