from django.db import models


class ResumeMatchResult(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="resume_matches",
        verbose_name="用户"
    )
    job = models.ForeignKey(
        "jobs.Job", on_delete=models.CASCADE, related_name="resume_matches",
        verbose_name="匹配岗位"
    )
    similarity_score = models.FloatField("相似度", default=0.0)
    matched_keywords = models.TextField("匹配关键词", blank=True, default="")
    created_at = models.DateTimeField("匹配时间", auto_now_add=True)

    class Meta:
        verbose_name = "简历匹配结果"
        verbose_name_plural = "简历匹配结果"
        ordering = ["-similarity_score"]

    def __str__(self):
        return f"{self.user.username} ↔ {self.job.title} ({self.similarity_score:.2f})"
