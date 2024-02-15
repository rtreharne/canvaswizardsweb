from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'front'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/<int:event_id>/', views.register, name='register'),
    path('portfolio/<int:portfolio_id>', views.portfolio, name='portfolio'),
    path('past/<int:event_id>/', views.register, name='past'),
    path('promo/<int:event_id>/', views.promo, name='promo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

