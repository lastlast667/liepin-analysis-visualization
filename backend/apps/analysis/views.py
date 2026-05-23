from django.db.models import Count, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.jobs.models import Job


@api_view(["GET"])
@permission_classes([AllowAny])
def company_analysis(request):
    """公司分析 API
    参数：
      - category: 岗位类别，多个用逗号分隔
      - partition: 地理分区，多个用逗号分隔
    返回：
      - statistics: 统计信息
      - industry_distribution: 行业分布 Top10
      - scale_distribution: 规模分布
      - companies: 在招岗位 Top10 公司
      - company_tags_cloud: 公司福利词云
      - category_options: 岗位类别选项列表
      - partition_options: 地理分区选项列表
    """
    # 获取 URL 里的查询参数
    category_param = request.query_params.get("category", "")
    partition_param = request.query_params.get("partition", "")

    # 查询所有数据
    queryset = Job.objects.all()
    
    if category_param:
        categories = [c.strip() for c in category_param.split(",") if c.strip()]
        if categories:
            queryset = queryset.filter(category__in=categories)

    if partition_param:
        partitions = [p.strip() for p in partition_param.split(",") if p.strip()]
        if partitions:
            queryset = queryset.filter(location_partition__in=partitions)

    # ── 统计：公司总数、覆盖行业总数、平均规模 ──

    companies_qs = (
        queryset.values("company_name", "company_industry", "company_scale", "company_link", "location_city")   # 公司名称、行业、规模、链接
        .annotate(job_count=Count("id"),)
        .order_by("-job_count")
    )
    total_companies = len(set(item["company_name"] for item in companies_qs))  # 公司总数(去重)

    industry_stats = (
        queryset.values("company_industry")
        .annotate(count=Count("company_industry"))
        .order_by("-count")
    )
    total_industries = industry_stats.count()  # 覆盖行业总数

    top_industry = None
    if industry_stats:
        first = industry_stats[0]
        top_industry = {"name": first["company_industry"] or "未知", "count": first["count"]}  # 占比最高行业

    scale_avg = 0
    has_scale = queryset.exclude(company_scale_min__isnull=True)
    if has_scale.exists():
        scale_avg = has_scale.aggregate(avg=Avg("company_scale_min"))["avg"] or 0
        scale_avg = round(scale_avg, 0)  # 平均规模

    # 主要规模类型
    scale_type = ""
    if scale_avg:
        if scale_avg < 1000:
            scale_type = "以小型企业为主"
        elif scale_avg < 5000:
            scale_type = "以中型企业为主"
        else:
            scale_type = "以大型企业为主"

    # ── 行业分布 Top 10 ──
    industry_top10 = industry_stats[:10]
    ind_total = sum(item["count"] for item in industry_top10) or 1
    industry_distribution = [
        {
            "name": item["company_industry"] or "未知",
            "count": item["count"],
            "percentage": round(item["count"] / ind_total * 100, 1),
        }
        for item in industry_top10
    ]

    # ── 规模分布 ──
    scale_stats = (
        queryset.values("company_scale")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    scale_distribution = [
        {"name": item["company_scale"] or "未知", "count": item["count"]}
        for item in scale_stats if item["company_scale"]
    ]

    # ── 省份分布 Top 10 + 其他 ──
    province_stats = (
        queryset.values("location_province")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    province_raw = [
        {"name": item["location_province"] or "未知", "count": item["count"]}
        for item in province_stats if item["location_province"]
    ]
    if len(province_raw) > 9:
        top9 = province_raw[:9]
        other_count = sum(item["count"] for item in province_raw[9:])
        province_distribution = top9 + [{"name": "其他省份", "count": other_count}]
    else:
        province_distribution = province_raw

    # ── 岗位数 Top 10 公司 ──
    company_data = {}
    for item in companies_qs:
        name = item["company_name"]
        if name not in company_data:
            company_data[name] = {
                "name": item["company_name"],
                "industry": item["company_industry"] or "未知",
                "scale": item["company_scale"] or "未知",
                "city": item["location_city"] or "未知",
                "jobs": item["job_count"],
            }
        else:
            exciting = company_data[name]
            if item["location_city"] not in exciting["city"]:
                company_data[name]["city"] = company_data[name]["city"] + "," + item["location_city"]
            company_data[name]["jobs"] += item["job_count"]

    company_list = sorted(list(company_data.values()), key=lambda x: x["jobs"], reverse=True)[:10]


    # ── 公司福利词云 ──
    all_tags = queryset.exclude(company_tags__isnull=True).exclude(company_tags=[]).values_list("company_tags", flat=True)
    tag_freq = {}
    for tags in all_tags:
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, str) and tag.strip():
                    tag_freq[tag.strip()] = tag_freq.get(tag.strip(), 0) + 1
    tag_cloud = sorted(
        [{"name": k, "value": v} for k, v in tag_freq.items()],
        key=lambda x: x["value"],
        reverse=True,
    )[:30]

    # ── 下拉框选项 ──
    category_options = [c[0] for c in Job.CategoryChoices.choices]
    partition_options = list(
        queryset.exclude(location_partition="")
        .values_list("location_partition", flat=True)
        .distinct()
        .order_by("location_partition")
    )

    return Response({
        "statistics": {
            "total_companies": total_companies,
            "total_industries": total_industries,
            "top_industry": top_industry,
            "avg_scale": scale_avg,
            "scale_type": scale_type,
        },
        "industry_distribution": industry_distribution,
        "scale_distribution": scale_distribution,
        "province_distribution": province_distribution,
        "companies": company_list,
        "company_tags_cloud": tag_cloud,
        "category_options": category_options,
        "partition_options": partition_options,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def location_distribution(request):
    """地区分布 API（待实现）"""
    return Response({})


@api_view(["GET"])
@permission_classes([AllowAny])
def job_search(request):
    """岗位搜索 API（待实现）"""
    return Response({"total": 0, "results": []})


@api_view(["GET"])
@permission_classes([AllowAny])
def salary_analysis(request):
    """薪资分析 API（待实现）"""
    return Response({"summary": {}, "by_category": [], "by_experience": [], "by_education": []})
