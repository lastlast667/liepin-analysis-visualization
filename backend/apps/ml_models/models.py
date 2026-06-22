from django.db import models


class MLModel(models.Model):
    MODEL_CHOICES = [
        ("salary_predictor", "薪资预测器"),
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
    """
    薪资预测模型
    """
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="用户")
    city = models.CharField("城市", max_length=100, blank=True, default="")
    category = models.CharField("岗位类别", max_length=100, blank=True, default="")
    experience_level = models.CharField("经验等级", max_length=50, blank=True, default="")
    education = models.CharField("学历", max_length=50, blank=True, default="")
    company_scale = models.CharField("公司规模", max_length=100, blank=True, default="")
    company_industry = models.CharField("公司行业", max_length=100, blank=True, default="")
    predicted_salary = models.IntegerField("预测薪资(K)", blank=True, null=True)
    predicted_min = models.IntegerField("预测最低薪资(K)", blank=True, null=True)
    predicted_max = models.IntegerField("预测最高薪资(K)", blank=True, null=True)
    model_used = models.CharField("使用的模型", max_length=100, blank=True, default="")
    feature_importance = models.JSONField("特征重要性", blank=True, default=list)
    created_at = models.DateTimeField("预测时间", auto_now_add=True)    # 自动添加创建时间字段

    class Meta:
        verbose_name = "薪资预测"
        verbose_name_plural = "薪资预测"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.city} {self.category} {self.experience_level} {self.predicted_min}-{self.predicted_max}K"


class RecommendationLog(models.Model):
    """
    推荐岗位模型
    """
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="recommendation_logs",
        verbose_name="用户"
    )
    results = models.JSONField("推荐结果", blank=True, default=list)  # [{"job_id": 1, "score": 0.8}, ...]
    strategy = models.CharField("推荐策略", max_length=20, blank=True, default="hybrid")
    created_at = models.DateTimeField("推荐时间", auto_now_add=True)

    class Meta:
        verbose_name = "推荐记录"
        verbose_name_plural = "推荐记录"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.strategy} ({len(self.results)} 条)"


class ResumeMatchResult(models.Model):
    """
    简历匹配结果模型
    """
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="resume_matches",
        verbose_name="用户"
    )
    results = models.JSONField("匹配结果", blank=True, default=dict)  # {"job_id": match_score, ...}
    total_count = models.IntegerField("匹配结果数", default=0)
    created_at = models.DateTimeField("匹配时间", auto_now_add=True)

    class Meta:
        verbose_name = "简历匹配结果"
        verbose_name_plural = "简历匹配结果"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 匹配 {self.total_count} 条结果"
