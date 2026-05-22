from django.db import models


class Job(models.Model):

    class CategoryChoices(models.TextChoices):
        JAVA = "Java开发", "Java开发"
        PYTHON = "Python开发", "Python开发"
        GO = "Go开发", "Go开发"
        CPP = "C++开发", "C++开发"
        PHP = "PHP开发", "PHP开发"
        CRAWLER = "爬虫工程师", "爬虫工程师"
        EMBEDDED = "嵌入式开发", "嵌入式开发"
        FRONTEND = "前端", "前端"
        FULLSTACK = "全栈", "全栈"
        OPS = "运维", "运维"
        ALGORITHM = "算法", "算法"

    class EducationChoices(models.TextChoices):
        JUNIOR_COLLEGE = "大专", "大专"
        BACHELOR = "本科", "本科"
        UNIFIED_BACHELOR = "统招本科", "统招本科"
        MASTER = "硕士", "硕士"
        PHD = "博士", "博士"
        NO_LIMIT = "学历不限", "学历不限"

    class ExperienceChoices(models.TextChoices):
        NO_LIMIT = "经验不限", "经验不限"
        INTERNSHIP = "实习", "实习"
        FRESH_GRAD = "应届", "应届"
        LESS_THAN_1Y = "1年以下", "1年以下"
        ABOVE_1Y = "1年以上", "1年以上"
        ABOVE_2Y = "2年以上", "2年以上"
        ABOVE_3Y = "3年以上", "3年以上"
        ABOVE_4Y = "4年以上", "4年以上"
        ABOVE_5Y = "5年以上", "5年以上"
        ABOVE_6Y = "6年以上", "6年以上"
        ABOVE_8Y = "8年以上", "8年以上"
        ABOVE_10Y = "10年以上", "10年以上"
        RANGE_1_3Y = "1-3年", "1-3年"
        RANGE_2_5Y = "2-5年", "2-5年"
        RANGE_3_5Y = "3-5年", "3-5年"
        RANGE_3_6Y = "3-6年", "3-6年"
        RANGE_5_10Y = "5-10年", "5-10年"
        RANGE_1_8Y = "1-8年", "1-8年"
        RANGE_2_8Y = "2-8年", "2-8年"
        RANGE_1_10Y = "1-10年", "1-10年"

    key = models.CharField("搜索关键词", max_length=50, blank=True, default="")
    job_url = models.URLField("岗位链接", blank=True, default="")
    title = models.CharField("岗位名称", max_length=255)
    salary = models.CharField("薪资文本", max_length=100, blank=True, default="")
    location = models.CharField("地点", max_length=255, blank=True, default="")
    experience = models.CharField("经验要求", max_length=50, blank=True, default="", choices=ExperienceChoices.choices)
    education = models.CharField("学历要求", max_length=50, blank=True, default="", choices=EducationChoices.choices)
    recruit_count = models.CharField("招聘人数(原始)", max_length=50, blank=True, default="")
    update_time = models.CharField("更新时间", max_length=50, blank=True, default="")
    company_name = models.CharField("公司名称", max_length=255, blank=True, default="")
    company_link = models.URLField("公司链接", blank=True, default="")
    company_industry = models.CharField("公司行业", max_length=255, blank=True, default="")
    company_scale = models.CharField("公司规模", max_length=100, blank=True, default="")
    company_scale_min = models.IntegerField("公司规模下限", blank=True, null=True)
    company_scale_max = models.IntegerField("公司规模上限", blank=True, null=True)
    job_description = models.TextField("岗位描述", blank=True, default="")
    language_requirement = models.CharField("语言要求", max_length=255, blank=True, default="")
    industry_requirement = models.CharField("行业要求", max_length=255, blank=True, default="")
    work_time = models.CharField("工作时间", max_length=255, blank=True, default="")
    company_tags = models.JSONField("公司标签", default=list, blank=True)
    crawl_time = models.DateTimeField("爬取时间", blank=True, null=True)

    month_salary_min = models.FloatField("月薪下限", blank=True, null=True)
    month_salary_max = models.FloatField("月薪上限", blank=True, null=True)
    month_salary_avg = models.FloatField("月薪均值", blank=True, null=True)
    location_city = models.CharField("城市", max_length=100, blank=True, default="")
    location_province = models.CharField("省份", max_length=100, blank=True, default="")
    category = models.CharField("岗位类别", max_length=100, blank=True, default="", choices=CategoryChoices.choices)
    tokenized_words = models.TextField("分词结果", blank=True, default="")

    recruit_count_parsed = models.IntegerField("招聘人数(解析)", blank=True, null=True)
    has_language_requirement = models.BooleanField("有外语要求", default=False)
    has_weekend_off = models.BooleanField("周末双休", default=False)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "岗位"
        verbose_name_plural = "岗位"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
