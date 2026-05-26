from collections import Counter, defaultdict

from django.db.models import Count, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.jobs.models import Job
from utils.load_words_from import load_words_from

@load_words_from("city_grade.txt")
def load_city_grade_map(words: list[str]) -> dict[str, str]:
    """
    加载城市-等级映射词表，返回城市-等级映射字典
    :param words: 城市-等级映射词表，每个元素为 "城市-等级" 格式
    :return: 城市-等级映射字典，键为城市，值为等级
    """
    city_grade = {}
    for word in words:
        city, grade = word.split(",")
        city_grade[city] = grade
    return city_grade

def calc_ratio(count, total):
    # 计算占比，保留1位小数，%表示
    return round(count / total * 100, 1) if total > 0 else 0.0

    

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
        queryset.values("company_name", "company_industry", "company_scale", "company_link", "location_city", "recruit_count_parsed")
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

    # ── 岗位数 Top 10 公司 + 招聘人数 Top 10 公司 ──
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
                "recruit_count_parsed": item["recruit_count_parsed"] or 1,
            }
        else:
            exciting = company_data[name]
            if item["location_city"] not in exciting["city"]:
                company_data[name]["city"] = company_data[name]["city"] + "," + item["location_city"]
            company_data[name]["recruit_count_parsed"] += (item["recruit_count_parsed"] or 1)   # 累加招聘人数，空值默认1
            company_data[name]["jobs"] += item["job_count"]                                     # 累加岗位数

    company_list_by_jobs = sorted(list(company_data.values()), key=lambda x: (x["jobs"], x["recruit_count_parsed"]), reverse=True)[:10]
    company_list_by_recruit = sorted(list(company_data.values()), key=lambda x: (x["recruit_count_parsed"], x["jobs"]), reverse=True)[:10]


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
    category_options = list(
        queryset.exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
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
        "companies_by_jobs": company_list_by_jobs,
        "companies_by_recruit": company_list_by_recruit,
        "company_tags_cloud": tag_cloud,
        "category_options": category_options,
        "partition_options": partition_options,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def location_distribution(request):
    """
    地区分布 API
    
    返回：
      - statistics: 统计信息
      - province_distribution: 省份分布
      - city_distribution: 城市分布
      - city_jobs_distribution: 城市岗位数分布
      - city_recruit_distribution: 城市招聘人数分布
      - partition_distribution: 分区分布
      - city_education_distribution: 城市学历分布
      - city_experience_distribution: 城市经验分布
    """

    # 查询所有数据
    jobs = list(Job.objects.values(
        "location_city", 
        "location_province",
        "location_partition", 
        "recruit_count_parsed", 
        "education", 
        "experience_level"
        ))

    # 加载城市-等级映射词表
    city_grade_map = load_city_grade_map()
    for job in jobs:
        job['city_grade'] = city_grade_map.get(job['location_city'], '其他')

    # ── 统计信息 ──
    total_cities = len(set([job['location_city'] for job in jobs]))  # 覆盖城市总数
    total_jobs = len(jobs)   # 总岗位数
    grade_counter = Counter([job['city_grade'] for job in jobs])    # 按等级统计岗位数
    
    # 计算等级分布占比，保留1位小数，%表示
    grade_ratio = {}
    for grade in grade_counter:
        grade_ratio[grade] = calc_ratio(grade_counter[grade], total_jobs)

    def get_top_city(grade):
        """找出各等级岗位数最多的城市"""
        grade_cities = [job['location_city'] for job in jobs if job['city_grade'] == grade]
        if not grade_cities:
            return "未知"
        return Counter(grade_cities).most_common(1)[0][0]
    

    # ── 省份岗位数量分布 ──
    province_counter = Counter([job['location_province'] for job in jobs])   # 按省份统计岗位数
    province_distribution = []
    for province, count in province_counter.items():
        province_distribution.append({"name": province, "value": count})

    def format_city_name(city_raw):
        """将原始城市名（如"北京""上海"）转换为前端要求的带"市"格式"""
        # 不需要加"市"的例外列表
        EXCLUDE_CITIES = {
            "香港", "澳门",
        }
        
        if city_raw in EXCLUDE_CITIES:
            return f"{city_raw}特别行政区"
        # 已经带"市"的直接返回，避免重复添加
        if city_raw.endswith("市"):
            return city_raw
        # 其他情况统一加"市"
        return f"{city_raw}市"
    
    # ── 城市岗位数量分布 ──
    city_counter = Counter([job['location_city'] for job in jobs])   # 按城市统计岗位数
    city_distribution = []
    for city, count in city_counter.items():
        city_distribution.append({"name": city, "value": count})
    city_jobs_distribution = sorted(city_distribution, key=lambda x: x['value'], reverse=True)  # 城市岗位数量排名

    
    # ── 省内城市岗位数量分布 ──
    city_to_province = {job['location_city']: job['location_province'] for job in jobs} # 城市-省份映射
    province_city_distribution = defaultdict(list)  # 字典类型存储城市-岗位数键值对
    for city_raw, job_count in city_counter.items():
        province = city_to_province[city_raw]   # 通过城市-省份映射获取省份
        city_formatted = format_city_name(city_raw)   # 格式化城市名称
        province_city_distribution[province].append({"name": city_formatted, "value": job_count})   # 存储城市-岗位数键值对到对应省份的列表中，每个元素为{"name": 城市名称, "value": 岗位数}
    province_city_distribution = dict(province_city_distribution)   # 转换为字典类型，键为省份，值为城市-岗位数键值对列表

    # ── 区域分布 ──
    all_partition = [job['location_partition'] for job in jobs]
    location_partition_counter = Counter(all_partition) # 按分区统计岗位数
    location_partition_ratio = {}
    for partition in location_partition_counter.keys():
        location_partition_ratio[partition] = calc_ratio(location_partition_counter[partition], total_jobs)

    # ── 主要城市学历要求分布 ──
    national_education = Counter()
    city_education_distribution_raw = defaultdict(Counter)

    for job in jobs:
        education = job['education']
        city = job['location_city']
        national_education[education] += 1
        city_education_distribution_raw[city][education] += 1
    
    city_education_distribution = {
        "全国": {
            education: calc_ratio(count, total_jobs) 
            for education, count in national_education.items()
        }
    }

    for city, count in city_education_distribution_raw.items():
        sum_count = sum(count.values())
        city_education_distribution[city] = {
            education: calc_ratio(count[education], sum_count) 
            for education in count.keys()
        }

    # ── 主要城市经验要求分布 ──
    national_experience = Counter()
    city_experience_distribution_raw = defaultdict(Counter)

    for job in jobs:
        experience = job['experience_level']
        city = job['location_city']
        national_experience[experience] += 1
        city_experience_distribution_raw[city][experience] += 1
    
    city_experience_distribution = {
        "全国": {
            experience: calc_ratio(count, total_jobs) 
            for experience, count in national_experience.items()
        }
    }

    for city, count in city_experience_distribution_raw.items():
        sum_count = sum(count.values())
        city_experience_distribution[city] = {
            experience: calc_ratio(count[experience], sum_count) 
            for experience in count.keys()
        }

    return Response({
        "statistics": {
            "total_cities": total_cities,
            "first_tier_ratio": grade_ratio.get('一线', 0),
            "first_tier_top_city": get_top_city('一线'),
            "new_first_tier_ratio": grade_ratio.get('新一线', 0),
            "new_first_tier_top_city": get_top_city('新一线'),
            "other_ratio": grade_ratio.get('其他', 0),
            "other_top_city": get_top_city('其他'),
            "location_partition_ratio": location_partition_ratio,
        },
        "province_distribution": province_distribution,   # 省份分布
        "province_city_distribution": province_city_distribution,   # 省内城市岗位数量分布
        "city_jobs_distribution": city_jobs_distribution,   # 城市岗位数量排名
        "partition_distribution": location_partition_ratio,   # 分区分布比例
        "city_education_distribution": city_education_distribution,   # 城市学历要求分布比例
        "city_experience_distribution": city_experience_distribution,   # 城市经验要求分布比例
    })


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


