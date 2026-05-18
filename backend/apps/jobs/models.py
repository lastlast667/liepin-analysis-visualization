from django.db import models


class Job(models.Model):
    title = models.CharField("岗位名称", max_length=255)
    company = models.CharField("公司名称", max_length=255, blank=True, default="")
    city = models.CharField("城市", max_length=100, blank=True, default="")
    category = models.CharField("岗位类别", max_length=100, blank=True, default="")
    salary_min = models.IntegerField("最低薪资(K)", blank=True, null=True)
    salary_max = models.IntegerField("最高薪资(K)", blank=True, null=True)
    salary_months = models.IntegerField("月数", blank=True, null=True)
    education = models.CharField("学历要求", max_length=50, blank=True, default="")
    experience = models.CharField("工作经验要求", max_length=50, blank=True, default="")
    description = models.TextField("岗位描述", blank=True, default="")
    labels = models.TextField("标签", blank=True, default="")
    source_url = models.URLField("来源URL", blank=True, default="")
    is_active = models.BooleanField("是否有效", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "岗位"
        verbose_name_plural = "岗位"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
