from django.contrib import admin
from .models import MLModel, SalaryPrediction


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ["name", "model_type", "accuracy", "f1_score", "is_active", "created_at"]
    list_filter = ["model_type", "is_active"]
    search_fields = ["name"]
    list_editable = ["is_active"]


@admin.register(SalaryPrediction)
class SalaryPredictionAdmin(admin.ModelAdmin):
    list_display = ["user", "city", "experience_years", "predicted_min", "predicted_max", "created_at"]
    list_filter = ["city"]
    search_fields = ["city", "user__username"]
