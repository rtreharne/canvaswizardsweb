from django.urls import path

from . import views

app_name = 'foundation2'
urlpatterns = [
    path('', views.start, name='start2'),
    path('question/', views.question, name='question2'),
    path('question/<int:question_id>', views.question, name='question2'),
    path('question/<int:question_id>/input', views.input, name='input2'),
    path('logout', views.logout_view, name='logout2'),
]