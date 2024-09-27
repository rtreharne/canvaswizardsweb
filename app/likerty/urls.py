from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from django.urls import re_path
from django.http import HttpResponse
from django.views.static import serve

from . import views

app_name = 'likerty'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('update-comment/', views.update_comment, name='update_comment'),
    path('logout', views.logout_view, name='logout'),
    path('dash', views.dash, name='dash'),
    path('like_response/', views.like_response, name='like_response'),
    path('dislike_response/', views.dislike_response, name='dislike_response'),
    path('hide_response/', views.hide_response, name='hide_response'),
    path('unhide_response/', views.unhide_response, name='unhide_response'),
    path('abuse_response/', views.abuse_response, name='abuse_response'),
    path('delete_response/', views.delete_response, name='delete_response'),
    path('<str:slug>/', views.response, name='response'),
    path('<str:slug>/share/', views.share, name='share'),
    path('<str:slug>/loop/', views.response_loop, name='response_loop'),
    path('<str:slug>/summary/', views.summary, name='summary'),
    path('<str:slug>/chat/', views.chat, name='chat'),
    path('<str:slug>/edit/', views.edit, name='edit')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

