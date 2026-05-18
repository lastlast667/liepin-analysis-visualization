from django.db import models


class SpiderTask(models.Model):
    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("running", "运行中"),
        ("completed", "已完成"),
        ("failed", "失败"),
    ]

    task_name = models.CharField("任务名称", max_length=255)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField("开始时间", blank=True, null=True)
    completed_at = models.DateTimeField("完成时间", blank=True, null=True)
    items_count = models.IntegerField("爬取数量", default=0)
    error_message = models.TextField("错误信息", blank=True, default="")

    class Meta:
        verbose_name = "爬虫任务"
        verbose_name_plural = "爬虫任务"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.task_name} [{self.get_status_display()}]"
