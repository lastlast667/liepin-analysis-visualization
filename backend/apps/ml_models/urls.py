from django.urls import path
from . import views

urlpatterns = [
    path('resume-match/options/', views.match_options, name='api_match_options'),
    path('resume-match/', views.match_resume, name='api_match_resume'),
    path('salary-predict/options/', views.salary_predict_options, name='api_salary_predict_options'),
    path('salary-predict/', views.salary_predict, name='api_salary_predict'),
]