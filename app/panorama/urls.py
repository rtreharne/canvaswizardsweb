from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'panorama'

urlpatterns = [
    path('', views.index, name='index'),
    path('<uuid:uuid>/', views.index, name='index-uuid'),
    path('download/<int:report_request_id>/', views.download_and_delete_file, name='download'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)