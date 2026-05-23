from django.contrib import admin
from django.urls import path, include

from .admin_views import DashboardView, SpiderControlView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/dashboard/", DashboardView.as_view(), name="admin_dashboard"),
    path("admin/spider-control/", SpiderControlView.as_view(), name="admin_spider_control"),

    # API
    path("api/auth/", include("apps.users.urls")),
    path("api/analysis/", include("apps.analysis.urls")),
]
