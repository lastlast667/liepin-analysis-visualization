from django.contrib import admin
from .models import MLModel, SalaryPrediction, RecommendationLog, ResumeMatchResult


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    """
    ML模型管理类
    """
    list_display = ["name", "model_type", "accuracy", "f1_score", "is_active", "created_at"]
    list_filter = ["model_type", "is_active"]
    search_fields = ["name"]
    list_editable = ["is_active"]


@admin.register(SalaryPrediction)
class SalaryPredictionAdmin(admin.ModelAdmin):
    """
    薪资预测模型管理类
    """
    list_display = ["user", "city", "category", "experience_years", "education", "work_time", "language_requirement", "predicted_min", "predicted_mid", "predicted_max", "created_at"]
    list_filter = ["city", "category", "experience_years", "education", "work_time", "language_requirement"]


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    """
    推荐岗位模型管理类
    """
    list_display = ["user", "job", "score", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ResumeMatchResult)
class ResumeMatchResultAdmin(admin.ModelAdmin):
    """
    简历匹配结果模型管理类
    """
    list_display = ["user", "job", "similarity_score", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False
