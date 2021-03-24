from . import views

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', views.index, name='index'),
    # ex: /quiz/5/
    path('<int:quiz_id>/', views.quiz_details, name='quiz_details'),
    # ex: /quiz/3/results/
    path('<int:quiz_id>/results/', views.results, name='results'),
    path('<int:quiz_id>/solutions/', views.solutions, name='solutions'),
]
