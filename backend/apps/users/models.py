from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField("手机号", max_length=20, blank=True, null=True, unique=True)
    avatar = models.URLField("头像", blank=True, default="")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    expected_city = models.CharField("期望城市", max_length=100, blank=True, default="")
    skills = models.TextField("技能标签", blank=True, default="")
    resume_text = models.TextField("简历文本", blank=True, default="")

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self):
        return f"{self.user.username} 的资料"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites", verbose_name="用户")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="favorited_by", verbose_name="岗位")
    created_at = models.DateTimeField("收藏时间", auto_now_add=True)

    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = "用户收藏"
        unique_together = ("user", "job")

    def __str__(self):
        return f"{self.user.username} → {self.job.title}"


class BrowseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="browse_history", verbose_name="用户")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="browse_history", verbose_name="岗位")
    browse_time = models.DateTimeField("浏览时间", auto_now_add=True)
    stay_duration = models.IntegerField("停留时长(秒)", default=0)

    class Meta:
        verbose_name = "浏览历史"
        verbose_name_plural = "浏览历史"
        ordering = ["-browse_time"]

    def __str__(self):
        return f"{self.user.username} → {self.job.title} ({self.browse_time})"
