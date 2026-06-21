"""
分析报告序列化器，负责数据校验（请求进来时）和数据格式转换（返回响应时）
数据校验：
前端发来的参数对不对？比如 page 必须是整数、 salary_min 必须是浮点数——Serializer 帮你自动校验，不用手写一堆 if not isinstance(...) 。
数据格式转换：
Python 的 datetime 、 Decimal 、模型对象这些类型不能直接 JSON 序列化。Serializer 帮你把它们转成 JSON 能认的格式。
"""
from rest_framework import serializers
from .models import AnalysisReport
from apps.jobs.models import Job


class AnalysisReportSerializer(serializers.ModelSerializer):
    """分析报告序列化器"""
    class Meta:
        model = AnalysisReport
        fields = "__all__"


class CompanyAnalysisSerializer(serializers.Serializer):
    """公司分析序列化器"""
    industry = serializers.CharField(required=False, allow_blank=True)
    scale = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)


class CompanyStatisticsSerializer(serializers.Serializer):
    """公司统计序列化器"""
    total_companies = serializers.IntegerField()
    avg_scale = serializers.FloatField()
    industry_count = serializers.IntegerField()


class CompanyIndustrySerializer(serializers.Serializer):
    """公司行业序列化器"""
    name = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class CompanyItemSerializer(serializers.Serializer):
    """公司项序列化器"""
    name = serializers.CharField()
    industry = serializers.CharField()
    scale = serializers.CharField()
    city = serializers.CharField()
    jobs = serializers.IntegerField()


class LocationDistributionSerializer(serializers.Serializer):
    """位置分布序列化器"""
    total_cities = serializers.IntegerField()
    tier1_ratio = serializers.FloatField()
    tier2_ratio = serializers.FloatField()


class JobSearchSerializer(serializers.Serializer):
    """岗位搜索序列化器"""
    keyword = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    salary_min = serializers.FloatField(required=False, allow_null=True)
    salary_max = serializers.FloatField(required=False, allow_null=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=20)


class SalaryAnalysisSerializer(serializers.Serializer):
    """薪资分析序列化器"""
    avg_salary = serializers.FloatField()
    median_salary = serializers.FloatField()
    max_salary = serializers.FloatField()
    salary_variance = serializers.FloatField()


class SalaryByCategorySerializer(serializers.Serializer):
    """薪资按分类序列化器"""
    name = serializers.CharField()
    salary = serializers.CharField()
    percentage = serializers.FloatField()


class SalaryByExperienceSerializer(serializers.Serializer):
    """薪资按经验序列化器"""
    level = serializers.CharField()
    min_salary = serializers.CharField()
    avg_salary = serializers.CharField()
    max_salary = serializers.CharField()
    range_pct = serializers.FloatField()
