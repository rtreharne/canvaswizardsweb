from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'front'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/<int:event_id>/', views.register, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

