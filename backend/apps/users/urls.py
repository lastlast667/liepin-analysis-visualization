from django.urls import path
from rest_framework.authtoken import views as auth_views
from . import views, admin_api

# 普通用户接口
urlpatterns = [
    path("test/", views.test_view, name="test"),
    path("login/", views.login_view, name="api_login"),
    path("register/", views.register_view, name="api_register"),
    path("logout/", views.logout_view, name="api_logout"),
    path("user/", views.user_info, name="api_user_info"),
    path("favorites/", views.favorites, name="api_favorites"),
    # path("favorites/add/", views.favorite_add, name="api_favorite_add"),
    path("favorites/<int:id>/", views.favorite_delete, name="api_favorite_delete"),
    path("browse_history/", views.browse_history, name="api_browse_history"),
    path("browse-history/", views.browse_history, name="api_browse_history_hyphen"),
    # path("browse-history/record/", views.record_browse, name="api_record_browse"),
    path("profile/", views.profile, name="api_profile"),
    path("password/", views.update_password, name="api_change_password"),
]

# 管理员接口
urlpatterns += [
    path("admin/stats/", admin_api.admin_stats, name="api_admin_stats"),
    path("admin/users/", admin_api.admin_users, name="api_admin_users"),
    path("admin/users/<int:id>/", admin_api.admin_user_delete, name="api_admin_user_delete"),
    path("admin/jobs/", admin_api.admin_jobs, name="api_admin_jobs"),
    path("admin/jobs/<int:id>/", admin_api.admin_job_delete, name="api_admin_job_delete"),
]
