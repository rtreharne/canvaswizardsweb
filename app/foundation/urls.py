from django.urls import path

from . import views

app_name = 'foundation'
urlpatterns = [
    path('', views.start, name='start'),
    path('<slug:slug>/', views.question, name='question'),
    path('<slug:slug>/question/<int:question_id>', views.question, name='question'),
    path('<slug:slug>/question/<int:question_id>/input', views.input, name='input'),
]