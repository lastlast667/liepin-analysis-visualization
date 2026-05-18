from django.contrib import admin
from .models import RecommendationLog


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ["user", "job", "score", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "job__title"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
