from django.db import models


class RecommendationLog(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="recommendation_logs",
        verbose_name="用户"
    )
    job = models.ForeignKey(
        "jobs.Job", on_delete=models.CASCADE, related_name="recommendation_logs",
        verbose_name="推荐岗位"
    )
    score = models.FloatField("推荐分数", default=0.0)
    created_at = models.DateTimeField("推荐时间", auto_now_add=True)

    class Meta:
        verbose_name = "推荐记录"
        verbose_name_plural = "推荐记录"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.job.title} ({self.score:.2f})"
