from django.db import models


class AnalysisReport(models.Model):
    REPORT_CHOICES = [
        ("salary", "薪资分析"),
        ("city", "城市分布"),
        ("category", "岗位类别"),
        ("trend", "趋势分析"),
        ("custom", "自定义"),
    ]

    report_type = models.CharField("报告类型", max_length=50, choices=REPORT_CHOICES)
    data = models.JSONField("报告数据", default=dict)
    generated_at = models.DateTimeField("生成时间", auto_now_add=True)

    class Meta:
        verbose_name = "分析报告"
        verbose_name_plural = "分析报告"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.get_report_type_display()} ({self.generated_at.strftime('%Y-%m-%d %H:%M')})"
