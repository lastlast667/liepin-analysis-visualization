from rest_framework import serializers
from .models import AnalysisReport
from apps.jobs.models import Job


class AnalysisReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisReport
        fields = "__all__"


class CompanyAnalysisSerializer(serializers.Serializer):
    """公司分析序列化器"""
    industry = serializers.CharField(required=False, allow_blank=True)
    scale = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)


class CompanyStatisticsSerializer(serializers.Serializer):
    total_companies = serializers.IntegerField()
    avg_scale = serializers.FloatField()
    industry_count = serializers.IntegerField()


class CompanyIndustrySerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class CompanyItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    industry = serializers.CharField()
    scale = serializers.CharField()
    city = serializers.CharField()
    jobs = serializers.IntegerField()


class LocationDistributionSerializer(serializers.Serializer):
    total_cities = serializers.IntegerField()
    tier1_ratio = serializers.FloatField()
    tier2_ratio = serializers.FloatField()


class JobSearchSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    salary_min = serializers.FloatField(required=False, allow_null=True)
    salary_max = serializers.FloatField(required=False, allow_null=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=20)


class SalaryAnalysisSerializer(serializers.Serializer):
    avg_salary = serializers.FloatField()
    median_salary = serializers.FloatField()
    max_salary = serializers.FloatField()
    salary_variance = serializers.FloatField()


class SalaryByCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    salary = serializers.CharField()
    percentage = serializers.FloatField()


class SalaryByExperienceSerializer(serializers.Serializer):
    level = serializers.CharField()
    min_salary = serializers.CharField()
    avg_salary = serializers.CharField()
    max_salary = serializers.CharField()
    range_pct = serializers.FloatField()
