from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "content_preview", "created_at"]
    list_filter = ["role", "user"]
    search_fields = ["content", "user__username"]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "消息摘要"

    readonly_fields = ["created_at"]
    list_per_page = 20

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
