from . import views

from django.contrib import admin
from django.urls import include, path

app_name = "quiz"
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name = 'signup'),
    # ex: /quiz/5/
    path('<int:quiz_id>/', views.quiz_details, name = 'quiz_details'),
    # ex: /quiz/3/results/
    path('results/', views.results, name = 'results'),
    path('<int:quiz_id>/results', views.result_details, name = 'result_details'),
    path('<int:quiz_id>/solutions/', views.solutions, name='solutions'),
]
