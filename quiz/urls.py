from . import views

from django.contrib import admin
from django.urls import include, path

app_name = "quiz"
urlpatterns = [
    path('', views.IndexView.as_view(), name = 'index'),
    path('signup/', views.SignupView.as_view(), name = 'signup'),
    path('<int:quiz_id>/', views.QuizDetailsView.as_view(), name = 'quiz_details'),
    path('results/', views.ResultsView.as_view(), name = 'results'),
    path('results/<int:quiz_id>/', views.ResultDetailsView.as_view(), name = 'result_details'),
]
