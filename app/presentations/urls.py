from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'presentations'

urlpatterns = [
    path('', views.index, name='index'),
    path('<uuid:uuid>/', views.showcase, name='index-uuid'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)