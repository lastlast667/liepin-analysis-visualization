from django.urls import path
from . import views

urlpatterns = [
    path("company/", views.company_analysis, name="api_company_analysis"),
    path("location/", views.location_distribution, name="api_location_distribution"),
    path("jobs/", views.job_search, name="api_job_search"),
    path("salary/", views.salary_analysis, name="api_salary_analysis"),
    path("jobs/<int:job_id>/", views.job_detail, name="api_job_detail"),
    path("dashboard/", views.get_dashboard, name="api_dashboard"),
]
