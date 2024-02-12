from django.urls import path

from . import views

app_name = 'lifesci'
urlpatterns = [
    path('', views.start, name='start2'),
    path('question/', views.question, name='question'),
    path('question/<int:question_id>', views.question, name='question'),
    path('question/<int:question_id>/input', views.input, name='input'),
    path('question/<int:question_id>/input/example', views.input, name='example'),
    path('logout', views.logout_view, name='logout'),
]