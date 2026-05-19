from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Favorite, BrowseHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "phone", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["username", "email", "phone"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("额外信息", {"fields": ["phone", "avatar"]}),
    )


class UserProfileInline(admin.StackedInline):
    """
    用户资料内联显示在用户管理页面
    """
    model = UserProfile
    can_delete = False
    verbose_name = "用户资料"
    verbose_name_plural = "用户资料"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "expected_city", "skills"]
    search_fields = ["user__username", "expected_city"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "job", "created_at"]
    list_filter = ["user"]
    search_fields = ["user__username", "job__title"]


@admin.register(BrowseHistory)
class BrowseHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "job", "browse_time", "stay_duration"]
    list_filter = ["user", "browse_time"]
    search_fields = ["user__username", "job__title"]
    date_hierarchy = "browse_time"
    list_per_page = 20
