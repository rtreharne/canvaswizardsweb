from django.urls import path

from . import views

app_name = 'staffsearch'
urlpatterns = [
    path('', views.index, name='index'),
    path('directory/', views.directory, name='directory')
]