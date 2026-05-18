from django.db import models


class MLModel(models.Model):
    MODEL_CHOICES = [
        ("salary_predictor", "薪资预测器"),
        ("text_classifier", "文本分类器"),
        ("recommender", "推荐模型"),
        ("resume_matcher", "简历匹配器"),
    ]

    name = models.CharField("模型名称", max_length=255)
    model_type = models.CharField("模型类型", max_length=50, choices=MODEL_CHOICES)
    accuracy = models.FloatField("准确率", blank=True, null=True)
    f1_score = models.FloatField("F1分数", blank=True, null=True)
    is_active = models.BooleanField("是否启用", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "ML模型"
        verbose_name_plural = "ML模型"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SalaryPrediction(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="用户"
    )
    city = models.CharField("城市", max_length=100, blank=True, default="")
    experience_years = models.IntegerField("工作经验(年)", default=0)
    education = models.CharField("学历", max_length=50, blank=True, default="")
    predicted_min = models.IntegerField("预测最低薪资(K)", blank=True, null=True)
    predicted_max = models.IntegerField("预测最高薪资(K)", blank=True, null=True)
    created_at = models.DateTimeField("预测时间", auto_now_add=True)

    class Meta:
        verbose_name = "薪资预测"
        verbose_name_plural = "薪资预测"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.city} {self.experience_years}年 {self.predicted_min}-{self.predicted_max}K"
