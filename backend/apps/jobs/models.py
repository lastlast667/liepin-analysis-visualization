from django.db import models


class Job(models.Model):

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

    class CompanyIndustryChoices(models.TextChoices):
        IT_SERVICE = "IT服务", "IT服务"
        TECHNICAL_SERVICE = "专业技术服务", "专业技术服务"
        CLOUD_BIG_DATA = "云计算/大数据", "云计算/大数据"
        INTERNET = "互联网", "互联网"
        HR_SERVICE = "人力资源服务", "人力资源服务"
        AI = "人工智能", "人工智能"
        INSTRUMENT = "仪器仪表", "仪器仪表"
        LOW_ALTITUDE_ECONOMY = "低空经济", "低空经济"
        INSURANCE = "保险", "保险"
        OTHER_BUSINESS = "其他商务服务业", "其他商务服务业"
        OTHER_LIFE_SERVICE = "其他生活服务", "其他生活服务"
        ROBOT = "具身智能与机器人", "具身智能与机器人"
        MEDICAL_DEVICE = "医疗器械", "医疗器械"
        MEDICAL_INSTITUTION = "医疗机构", "医疗机构"
        CONSULTING = "咨询服务", "咨询服务"
        ONLINE_EDUCATION = "在线教育", "在线教育"
        SOCIAL_MEDIA = "在线社交/媒体", "在线社交/媒体"
        TRAINING = "培训服务", "培训服务"
        SECURITIES = "基金/证券/期货", "基金/证券/期货"
        RESEARCH = "学术/科研", "学术/科研"
        INDOOR_ENTERTAINMENT = "室内娱乐", "室内娱乐"
        INDUSTRIAL_AUTOMATION = "工业自动化", "工业自动化"
        ADVERTISING = "广告/公关/会展", "广告/公关/会展"
        BROADCASTING = "广播/影视/录音", "广播/影视/录音"
        REAL_ESTATE_DEV = "房地产开发经营", "房地产开发经营"
        REAL_ESTATE_RENT = "房地产租赁/中介", "房地产租赁/中介"
        WHOLESALE_RETAIL = "批发/零售", "批发/零售"
        GOVERNMENT = "政府/公共事业", "政府/公共事业"
        VEHICLE_MANUFACTURE = "整车制造", "整车制造"
        CULTURAL_ART = "文化艺术业", "文化艺术业"
        NEW_MATERIAL = "新材料", "新材料"
        NEW_ENERGY = "新能源", "新能源"
        NEW_ENERGY_VEHICLE = "新能源汽车", "新能源汽车"
        NEWS_PUBLISH = "新闻和出版业", "新闻和出版业"
        SMART_HARDWARE = "智能硬件/消费电子", "智能硬件/消费电子"
        MACHINERY = "机械/设备", "机械/设备"
        INSPECTION = "检测/认证", "检测/认证"
        AUTO_PARTS = "汽车零部件及配件", "汽车零部件及配件"
        GAME = "游戏", "游戏"
        PROPERTY_MGMT = "物业/商业管理", "物业/商业管理"
        ENVIRONMENTAL = "环保", "环保"
        LIFE_SERVICE_O2O = "生活服务O2O", "生活服务O2O"
        ENERGY_UTILITY = "电力/热力/燃气/水务", "电力/热力/燃气/水务"
        ELECTRONICS = "电子/半导体/集成电路", "电子/半导体/集成电路"
        ECOMMERCE = "电子商务", "电子商务"
        ELECTRICAL = "电气机械/器材", "电气机械/器材"
        TECH_PROMOTION = "科技推广服务", "科技推广服务"
        TECH_FINANCE = "科技金融", "科技金融"
        CYBER_SECURITY = "网络/信息安全", "网络/信息安全"
        AEROSPACE = "航空/航天设备", "航空/航天设备"
        FORFAITING = "融资租赁/保理", "融资租赁/保理"
        COMPUTER_HARDWARE = "计算机硬件", "计算机硬件"
        COMPUTER_SOFTWARE = "计算机软件", "计算机软件"
        LOGISTICS = "货运/物流/仓储", "货运/物流/仓储"
        TRADE = "贸易/进出口", "贸易/进出口"
        ASSET_MGMT = "资产管理", "资产管理"
        TELECOM = "通信设备", "通信设备"
        HOTEL = "酒店/民宿", "酒店/民宿"
        FOOD_BEVERAGE = "食品/饮料/酒水", "食品/饮料/酒水"
    
    class CompanyScaleChoices(models.TextChoices):
        BETWEEN_1_49 = "1-49人", "1-49人"
        BETWEEN_50_99 = "50-99人", "50-99人"
        BETWEEN_100_499 = "100-499人", "100-499人"
        BETWEEN_500_999 = "500-999人", "500-999人"
        BETWEEN_1000_2000 = "1000-2000人", "1000-2000人"
        BETWEEN_2000_5000 = "2000-5000人", "2000-5000人"
        BETWEEN_5000_10000 = "5000-10000人", "5000-10000人"
        ABOVE_100000 = "10000人以上", "10000人以上"

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
    location_partition = models.CharField("分区", max_length=100, blank=True, default="")
    category = models.CharField("岗位类别", max_length=100, blank=True, default="")
    tokenized_words = models.TextField("分词结果", blank=True, default="")
    experience_level = models.CharField("经验等级", max_length=50, blank=True, default="")

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
