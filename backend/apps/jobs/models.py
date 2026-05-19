from django.db import models


class Job(models.Model):
    key = models.CharField("搜索关键词", max_length=50, blank=True, default="")
    job_url = models.URLField("岗位链接", blank=True, default="")
    title = models.CharField("岗位名称", max_length=255)
    salary = models.CharField("薪资文本", max_length=100, blank=True, default="")
    location = models.CharField("地点", max_length=255, blank=True, default="")
    experience = models.CharField("经验要求", max_length=50, blank=True, default="")
    education = models.CharField("学历要求", max_length=50, blank=True, default="")
    recruit_count = models.CharField("招聘人数", max_length=50, blank=True, default="")
    update_time = models.CharField("更新时间", max_length=50, blank=True, default="")
    company_name = models.CharField("公司名称", max_length=255, blank=True, default="")
    company_link = models.URLField("公司链接", blank=True, default="")
    job_description = models.TextField("岗位描述", blank=True, default="")
    language_requirement = models.CharField("语言要求", max_length=255, blank=True, default="")
    industry_requirement = models.CharField("行业要求", max_length=255, blank=True, default="")
    work_time = models.CharField("工作时间", max_length=255, blank=True, default="")
    company_tags = models.JSONField("公司标签", default=list, blank=True)
    crawl_time = models.DateTimeField("爬取时间", blank=True, null=True)

    month_salary_min = models.FloatField("月薪下限", blank=True, null=True)
    month_salary_max = models.FloatField("月薪上限", blank=True, null=True)
    location_city = models.CharField("城市", max_length=100, blank=True, default="")
    location_province = models.CharField("省份", max_length=100, blank=True, default="")
    category = models.CharField("岗位类别", max_length=100, blank=True, default="")
    tokenized_words = models.TextField("分词结果", blank=True, default="")

    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "岗位"
        verbose_name_plural = "岗位"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
