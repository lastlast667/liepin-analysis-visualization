from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company_name", "location", "salary", "category", "experience", "education", "recruit_count_parsed", "has_weekend_off", "crawl_time"]
    list_filter = ["category", "location_city", "experience", "education", "has_language_requirement", "has_weekend_off"]
    search_fields = ["title", "company_name", "job_description"]
    ordering = ["-created_at"]
    date_hierarchy = "crawl_time"

    fieldsets = [
        ("基本信息", {"fields": ["key", "job_url", "title", "salary"]}),
        ("公司信息", {"fields": ["company_name", "company_link", "company_tags"]}),
        ("地点信息", {"fields": ["location", "location_city", "location_province"]}),
        ("任职要求", {"fields": ["experience", "education", "recruit_count", "recruit_count_parsed"]}),
        ("岗位描述", {"fields": ["job_description"]}),
        ("其他信息", {"fields": ["language_requirement", "has_language_requirement", "industry_requirement", "work_time", "has_weekend_off", "update_time", "crawl_time"]}),
        ("分析数据", {"fields": ["month_salary_min", "month_salary_max", "category", "tokenized_words"]}),
    ]

    readonly_fields = ["crawl_time", "created_at"]
    list_per_page = 10

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
