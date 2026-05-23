from django.db.models import Count, Avg, Max, Min, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.jobs.models import Job
from .models import AnalysisReport
from .serializers import (
    CompanyStatisticsSerializer,
    CompanyIndustrySerializer,
    CompanyItemSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def company_analysis(request):
    """公司分析 API"""
    industry = request.query_params.get("industry", "")
    scale = request.query_params.get("scale", "")
    city = request.query_params.get("city", "")

    queryset = Job.objects.all()

    if industry:
        queryset = queryset.filter(company_industry__icontains=industry)
    if city:
        queryset = queryset.filter(location_city__icontains=city)

    companies = (
        queryset.values("company_name", "company_industry", "company_scale", "location_city")
        .annotate(job_count=Count("id"))
        .order_by("-job_count")
    )

    total_companies = companies.count()
    avg_scale = 0
    if total_companies > 0:
        scale_queryset = queryset.exclude(company_scale_min__isnull=True)
        if scale_queryset.exists():
            avg_scale = scale_queryset.aggregate(avg=Avg("company_scale_min"))["avg"] or 0

    industry_stats = (
        queryset.values("company_industry")
        .annotate(count=Count("company_industry", distinct=True))
        .order_by("-count")
    )
    industry_count = industry_stats.count()

    industry_top10 = industry_stats[:10]
    total = sum(item["count"] for item in industry_top10) or 1
    industry_data = [
        {
            "name": item["company_industry"] or "未知",
            "count": item["count"],
            "percentage": round(item["count"] / total * 100, 1),
        }
        for item in industry_top10
    ]

    company_list = [
        {
            "name": item["company_name"],
            "industry": item["company_industry"] or "未知",
            "scale": item["company_scale"] or "未知",
            "city": item["location_city"] or "未知",
            "jobs": item["job_count"],
        }
        for item in companies[:20]
    ]

    stats = {
        "total_companies": total_companies,
        "avg_scale": round(avg_scale, 0),
        "industry_count": industry_count,
    }

    return Response({
        "statistics": stats,
        "industry_distribution": industry_data,
        "companies": company_list,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def location_distribution(request):
    """地区分布 API"""
    queryset = Job.objects.all()

    city = request.query_params.get("city", "")
    if city:
        queryset = queryset.filter(location_city__icontains=city)

    city_stats = (
        queryset.values("location_city")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    total_cities = city_stats.count()
    total = sum(item["count"] for item in city_stats) or 1

    tier1_cities = {"北京", "上海", "深圳", "广州"}
    tier2_cities = {"杭州", "成都", "武汉", "南京", "西安", "长沙"}

    tier1_count = sum(item["count"] for item in city_stats if item["location_city"] in tier1_cities)
    tier2_count = sum(item["count"] for item in city_stats if item["location_city"] in tier2_cities)

    city_data = [
        {
            "name": item["location_city"] or "未知",
            "count": item["count"],
            "percentage": round(item["count"] / total * 100, 1),
            "tag": "一线" if item["location_city"] in tier1_cities else ("新一线" if item["location_city"] in tier2_cities else ""),
        }
        for item in city_stats[:20]
    ]

    region_cities = {
        "华东地区": {"上海", "杭州", "南京", "苏州", "宁波", "合肥", "无锡"},
        "华北地区": {"北京", "天津", "石家庄", "太原", "济南", "青岛"},
        "华南地区": {"深圳", "广州", "东莞", "佛山", "珠海", "厦门", "福州"},
        "西南地区": {"成都", "重庆", "昆明", "贵阳"},
        "华中地区": {"武汉", "长沙", "郑州", "南昌"},
    }

    all_mapped_cities = set()
    for cities in region_cities.values():
        all_mapped_cities.update(cities)

    region_data = []
    for region_name, cities in region_cities.items():
        region_count = sum(
            item["count"] for item in city_stats
            if item["location_city"] in cities
        )
        if region_count > 0:
            region_data.append({
                "name": region_name,
                "percentage": round(region_count / total * 100, 1),
            })

    other_count = sum(
        item["count"] for item in city_stats
        if item["location_city"] and item["location_city"] not in all_mapped_cities
    )
    if other_count > 0:
        region_data.append({
            "name": "其他地区",
            "percentage": round(other_count / total * 100, 1),
        })

    return Response({
        "total_cities": total_cities,
        "tier1_ratio": round(tier1_count / total * 100, 1),
        "tier2_ratio": round(tier2_count / total * 100, 1),
        "cities": city_data,
        "regions": region_data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def job_search(request):
    """岗位搜索 API"""
    keyword = request.query_params.get("keyword", "")
    city = request.query_params.get("city", "")
    salary_min = request.query_params.get("salary_min")
    salary_max = request.query_params.get("salary_max")
    experience = request.query_params.get("experience", "")
    category = request.query_params.get("category", "")
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 20))

    queryset = Job.objects.all()

    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword) | Q(job_description__icontains=keyword)
        )
    if city:
        queryset = queryset.filter(location_city__icontains=city)
    if salary_min:
        queryset = queryset.filter(month_salary_min__gte=float(salary_min))
    if salary_max:
        queryset = queryset.filter(month_salary_max__lte=float(salary_max))
    if experience:
        queryset = queryset.filter(experience=experience)
    if category:
        queryset = queryset.filter(category=category)

    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    jobs = queryset[start:end]

    job_list = [
        {
            "title": job.title,
            "company": job.company_name,
            "location": f"{job.location_city or ''} {job.location or ''}".strip(),
            "salary": job.salary,
            "salary_min": job.month_salary_min,
            "salary_max": job.month_salary_max,
            "experience": job.experience,
            "education": job.education,
            "category": job.category,
            "update_time": job.update_time,
        }
        for job in jobs
    ]

    return Response({
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": job_list,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def salary_analysis(request):
    """薪资分析 API"""
    queryset = Job.objects.filter(month_salary_avg__isnull=False)

    category = request.query_params.get("category", "")
    city = request.query_params.get("city", "")
    if category:
        queryset = queryset.filter(category=category)
    if city:
        queryset = queryset.filter(location_city__icontains=city)

    salary_data = queryset.aggregate(
        avg_salary=Avg("month_salary_avg"),
        max_salary=Max("month_salary_avg"),
        min_salary=Min("month_salary_avg"),
    )

    all_salaries = list(queryset.values_list("month_salary_avg", flat=True))
    sorted_salaries = sorted(all_salaries)
    n = len(sorted_salaries)

    median_salary = sorted_salaries[n // 2] if n > 0 else 0
    if n > 0 and n % 2 == 0:
        median_salary = (sorted_salaries[n // 2 - 1] + sorted_salaries[n // 2]) / 2

    variance = 0
    if n > 0 and salary_data["avg_salary"]:
        variance = round(
            sum((s - salary_data["avg_salary"]) ** 2 for s in all_salaries) / n, 2
        )

    category_data = (
        queryset.values("category")
        .annotate(avg=Avg("month_salary_avg"), count=Count("id"))
        .order_by("-avg")
    )
    max_avg = max((item["avg"] or 0) for item in category_data) or 1
    salary_by_category = [
        {
            "name": item["category"] or "未知",
            "salary": f"¥{item['avg']:,.0f}" if item["avg"] else "N/A",
            "percentage": round((item["avg"] or 0) / max_avg * 100, 1),
        }
        for item in category_data
    ]

    experience_order = [
        "应届", "1年以下", "1年以上", "1-3年", "2年以上",
        "2-5年", "3年以上", "3-5年", "3-6年", "4年以上",
        "5年以上", "5-10年", "6年以上", "8年以上", "10年以上",
    ]
    experience_data = (
        queryset.values("experience")
        .annotate(avg=Avg("month_salary_avg"))
        .order_by("-avg")
    )

    salary_by_exp = [
        {
            "level": item["experience"] or "未知",
            "min_salary": f"¥{item['avg'] * 0.6:,.0f}" if item["avg"] else "N/A",
            "avg_salary": f"¥{item['avg']:,.0f}" if item["avg"] else "N/A",
            "max_salary": f"¥{item['avg'] * 1.4:,.0f}" if item["avg"] else "N/A",
            "range_pct": round((item["avg"] or 0) / ((salary_data["max_salary"] or 1)) * 100, 1),
        }
        for item in experience_data
    ]

    education_data = (
        queryset.values("education")
        .annotate(avg=Avg("month_salary_avg"))
        .order_by("-avg")
    )
    max_edu_avg = max((item["avg"] or 0) for item in education_data) or 1
    salary_by_edu = [
        {
            "name": item["education"] or "未知",
            "salary": f"¥{item['avg']:,.0f}" if item["avg"] else "N/A",
            "ratio": round((item["avg"] or 0) / max_edu_avg * 100, 1),
        }
        for item in education_data
    ]

    return Response({
        "summary": {
            "avg_salary": round(salary_data["avg_salary"] or 0, 0),
            "median_salary": round(median_salary, 0),
            "max_salary": round(salary_data["max_salary"] or 0, 0),
            "salary_variance": variance,
        },
        "by_category": salary_by_category,
        "by_experience": salary_by_exp,
        "by_education": salary_by_edu,
    })
