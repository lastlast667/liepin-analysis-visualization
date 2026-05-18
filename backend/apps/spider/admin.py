from django.contrib import admin
from .models import SpiderTask


@admin.register(SpiderTask)
class SpiderTaskAdmin(admin.ModelAdmin):
    list_display = ["task_name", "status", "started_at", "completed_at", "items_count"]
    list_filter = ["status"]
    search_fields = ["task_name"]
    readonly_fields = ["started_at", "completed_at"]

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
