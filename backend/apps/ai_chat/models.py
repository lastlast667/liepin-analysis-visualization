from django.db import models


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "用户"),
        ("assistant", "AI助手"),
    ]

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="chat_messages",
        verbose_name="用户"
    )
    role = models.CharField("角色", max_length=20, choices=ROLE_CHOICES)
    content = models.TextField("消息内容")
    created_at = models.DateTimeField("发送时间", auto_now_add=True)

    class Meta:
        verbose_name = "对话消息"
        verbose_name_plural = "对话消息"
        ordering = ["created_at"]

    def __str__(self):
        prefix = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"[{self.get_role_display()}] {prefix}"
