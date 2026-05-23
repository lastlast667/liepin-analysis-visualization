from django.urls import path
from . import views

urlpatterns = [
    path("company/", views.company_analysis, name="api_company_analysis"),
    path("location/", views.location_distribution, name="api_location_distribution"),
    path("jobs/", views.job_search, name="api_job_search"),
    path("salary/", views.salary_analysis, name="api_salary_analysis"),
]
