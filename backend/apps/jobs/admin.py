from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "city", "category", "salary_min", "salary_max", "is_active", "created_at"]
    list_filter = ["category", "city", "education", "experience"]
    search_fields = ["title", "company", "description"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = [
        ("基础信息", {"fields": ["title", "company", "city"]}),
        ("薪资信息", {"fields": ["salary_min", "salary_max", "salary_months"]}),
        ("分类标签", {"fields": ["category", "labels"]}),
        ("任职要求", {"fields": ["education", "experience"]}),
        ("文本内容", {"fields": ["description"]}),
        ("元信息", {"fields": ["source_url", "is_active"]}),
    ]

    readonly_fields = ["source_url", "created_at", "updated_at"]
    list_per_page = 20

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
