from django.urls import path
from rest_framework.authtoken import views as auth_views
from . import views

urlpatterns = [
    path("test/", views.test_view, name="test"),
    path("login/", views.login_view, name="api_login"),
    path("register/", views.register_view, name="api_register"),
    path("logout/", views.logout_view, name="api_logout"),
    path("user/", views.user_info, name="api_user_info"),
]
