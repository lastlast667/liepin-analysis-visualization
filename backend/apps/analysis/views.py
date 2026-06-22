from collections import Counter, defaultdict
from io import BytesIO
from statistics import median

from django.db.models import Q, Case, Count, Avg, Max, Min, Sum, Value, When
from django.forms import IntegerField, model_to_dict
import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
import base64
import matplotlib
from apps.analysis.recommenders.engine import recommend
matplotlib.use('Agg')  # 使用非交互式后端，避免在Django线程中启动GUI
import seaborn as sns
import matplotlib.pyplot as plt

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

def get_distinct_options(queryset, field_name):
    """
    从查询集中获取指定字段的唯一值，排除空值
    排序逻辑完全交给前端处理

    Args:
        queryset: 基础查询集
        field_name: 要获取的字段名

    Returns:
        list: 去重后的选项列表
    """
    return list(
        queryset
        # 同时排除空字符串和NULL两种空值
        .exclude(**{f"{field_name}__in": ["", None]})
        # 只取指定字段，返回纯字符串列表
        .values_list(field_name, flat=True)
        # 去重
        .distinct()
        # 按字段本身排序
        .order_by(field_name)
    )

def get_cached_options(base_queryset, field_name, timeout=3600):
    """
    带缓存的下拉框选项生成函数
    排序逻辑完全交给前端处理

    Args:
        base_queryset: 基础查询集
        field_name: 要获取的字段名
        timeout: 缓存过期时间，单位秒，默认1小时

    Returns:
        list: 去重后的选项列表
    """
    # 生成唯一的缓存键
    cache_key = f"job_options:{field_name}"
    
    # 先尝试从缓存中获取
    options = cache.get(cache_key)
    
    # 缓存中没有则从数据库查询，并写入缓存
    if options is None:
        options = get_distinct_options(base_queryset, field_name)
        cache.set(cache_key, options, timeout)
    
    return options

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

    # 全量数据（用于提取下拉选项和右侧统计栏，不受筛选影响）
    base_queryset = Job.objects.all()
    # 筛选数据（用于岗位结果）
    queryset = base_queryset
    
    if category_param:
        categories = [c.strip() for c in category_param.split(",") if c.strip()]
        if categories:
            queryset = base_queryset.filter(category__in=categories)

    if partition_param:
        partitions = [p.strip() for p in partition_param.split(",") if p.strip()]
        if partitions:
            queryset = base_queryset.filter(location_partition__in=partitions)

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
    category_options = get_cached_options(base_queryset, "category")
    partition_options = get_cached_options(base_queryset, "location_partition")

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
    # 统计全国和各城市的岗位数，按学历要求分类
    for job in jobs:
        education = job['education']
        city = job['location_city']
        national_education[education] += 1
        city_education_distribution_raw[city][education] += 1
    
    # 默认全国学历要求分布比例
    city_education_distribution = {
        "全国": {
            education: calc_ratio(count, total_jobs) 
            for education, count in national_education.items()
        }
    }
    # 计算每个城市的学历要求分布比例
    for city, count in city_education_distribution_raw.items():
        sum_count = sum(count.values())
        city_education_distribution[city] = {
            education: calc_ratio(count[education], sum_count) 
            for education in count.keys()
        }

    # ── 主要城市经验要求分布 ──
    national_experience = Counter()
    city_experience_distribution_raw = defaultdict(Counter)

    # 统计全国和各城市的岗位数，按经验等级分类
    for job in jobs:
        experience = job['experience_level']
        city = job['location_city']
        national_experience[experience] += 1
        city_experience_distribution_raw[city][experience] += 1
    
    # 默认全国经验要求分布比例
    city_experience_distribution = {
        "全国": {
            experience: calc_ratio(count, total_jobs) 
            for experience, count in national_experience.items()
        }
    }
    # 计算每个城市的经验要求分布比例
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
    """
    岗位列表 API
    参数：
      - keyword: 岗位关键词
      - city: 城市名称
      - salary: 薪资范围
      - education: 学历要求
      - experience_level: 经验要求
      - sort_by: 排序字段(默认"default"综合)、 salary (薪资降序)、 experience (经验)、 education (学历)
      - page: 页码 (default 1)
      - page_size: 每页条数 (default 10)

    返回：
      - total: 岗位总数
      - page: 当前页码
      - page_size: 每页条数
      - total_pages: 总页数

      - results: 岗位列表
        - 每个岗位包含以下字段：
          - id: 岗位ID
          - title: 岗位标题
          - company_name: 公司名称
          - salary: 薪资
          - month_salary_avg: 平均月薪资
          - location_city: 城市
          - education: 学历
          - experience: 经验
          - experience_level: 经验等级
          - recruit_count: 招聘人数
          - recruit_count_parsed: 招聘人数解析后的整数
          - company_industry: 公司行业
          - update_time: 更新时间
      
      - city_options: 可选的城市列表
        - 每个城市包含以下字段：
          - city: 城市名称
      - education_options: 可选的学历要求列表
        - 每个学历包含以下字段：
          - education: 学历要求
      - experience_level_options: 可选的经验等级列表
        - 每个经验等级包含以下字段：
          - experience_level: 经验等级
    
      - hot_jobs: 热门岗位列表
        - 每个岗位包含以下字段：
          - id: 岗位ID
          - title: 岗位标题
          - company_name: 公司名称
          - salary: 薪资
          - month_salary_avg: 平均月薪资

      - hot_cities: 热门城市列表
        - 每个城市包含以下字段：
          - name: 城市名称
          - count: 岗位数量

      - hot_companies: 热门公司列表
        - 每个公司包含以下字段：
          - name: 公司名称
          - count: 岗位数量
    """

    # 获取URL里的参数
    keyword = request.query_params.get("keyword")
    location_city = request.query_params.get("location_city")
    salary = request.query_params.get("salary")
    education = request.query_params.get("education")
    experience_level = request.query_params.get("experience_level")
    company_name = request.query_params.get("company_name")
    sort_by = request.query_params.get("sort_by", "default")
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 全量数据（用于提取下拉选项和右侧统计栏，不受筛选影响）
    base_queryset = Job.objects.all()
    # 筛选数据（用于岗位结果）
    queryset = base_queryset

    # 筛选公司名称（用于公司详情页）
    if company_name:
        queryset = queryset.filter(company_name=company_name)

    # 筛选岗位关键词
    if keyword:
        queryset = queryset.filter(Q(title__icontains=keyword) | Q(company_name__icontains=keyword))

    # 筛选城市
    if location_city:
        queryset = queryset.filter(location_city=location_city)

    # 薪资范围筛选（基于 month_salary_avg 字段做范围过滤）
    if salary:
        if salary == "10k以内":
            queryset = queryset.filter(month_salary_avg__lt=10000)  # 小于10k
        elif salary == "10-20k":
            queryset = queryset.filter(month_salary_avg__gte=10000, month_salary_avg__lt=20000)  # 大于等于10k，小于20k
        elif salary == "20-30k":
            queryset = queryset.filter(month_salary_avg__gte=20000, month_salary_avg__lt=30000)  # 大于等于20k，小于30k
        elif salary == "30-50k":
            queryset = queryset.filter(month_salary_avg__gte=30000, month_salary_avg__lt=50000)  # 大于等于30k，小于50k
        elif salary == "50k以上":
            queryset = queryset.filter(month_salary_avg__gte=50000)  # 大于等于50k
        elif salary == "薪资面议":
            queryset = queryset.filter(month_salary_avg__isnull=True)  # 空值表示薪资面议

    # 学历筛选
    if education:
        queryset = queryset.filter(education=education)

    # 经验筛选
    if experience_level:
        queryset = queryset.filter(experience_level=experience_level)

    # 统计岗位总数和总页数
    total = queryset.count()
    total_pages = (total + page_size - 1) // page_size

    # 排序
    education_order = Case(
        When(education="博士", then=Value(0)),
        When(education="硕士", then=Value(1)),
        When(education="统招本科", then=Value(2)),
        When(education="本科", then=Value(3)),
        When(education="专科", then=Value(4)),
        default=Value(5),
    )
    experience_order = Case(
        When(experience_level="5-10年", then=Value(0)),
        When(experience_level="3-5年", then=Value(1)),
        When(experience_level="1-3年", then=Value(2)),
        When(experience_level="应届生", then=Value(3)),
        When(experience_level="实习生", then=Value(4)),
        default=Value(5),
    )
    sort_mapping = {
        "default": ["-id"],
        "salary": ["-month_salary_avg"],
        "experience": [experience_order],
        "education": [education_order],
    }
    queryset = queryset.order_by(*sort_mapping.get(sort_by, sort_mapping["default"]))

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    page_queryset = queryset[start:end]

    jobs = list(page_queryset.values(
        "id", "title", 
        "company_name", 
        "salary", 
        "month_salary_avg", 
        "location_city", 
        "education", 
        "experience", 
        "experience_level", 
        "recruit_count", 
        "recruit_count_parsed", 
        "company_industry", 
        "update_time_parsed",
        ))
    
    for job in jobs:
        job["update_time_parsed"] = job["update_time_parsed"].strftime("%Y-%m-%d")
    
    # —— 下拉框选项 ——
    city_options = get_cached_options(base_queryset, "location_city")
    education_options = get_cached_options(base_queryset, "education")
    experience_level_options = get_cached_options(base_queryset, "experience_level")

    # —— 热门岗位列表 Top5 ——
    hot_jobs = list(
        base_queryset.values("id", "title", "company_name", "salary", "month_salary_avg")
        .order_by("-month_salary_avg")[:5]
    )

    # —— 热门城市列表 Top10 ——    
    hot_cities_raw = list(base_queryset.values_list("location_city", flat=True))
    # 统计各城市的岗位数
    city_distribution_raw = Counter(hot_cities_raw)
    
    # 所有城市岗位数降序排序
    hot_cities = sorted(city_distribution_raw.items(), key=lambda x: x[1], reverse=True)[:10]
    # 转换为列表，每个元素为字典，包含城市名称和岗位数
    hot_cities = [{"name": city, "count": count} for city, count in hot_cities]

    # —— 热门公司列表 Top5 ——
    hot_companies_raw = list(base_queryset.values_list("company_name", flat=True))
    # 统计各公司的岗位数
    company_distribution_raw = Counter(hot_companies_raw)
    
    # 所有公司岗位数降序排序
    hot_companies = sorted(company_distribution_raw.items(), key=lambda x: x[1], reverse=True)[:5]
    # 转换为列表，每个元素为字典，包含公司名称和岗位数
    hot_companies = [{"name": company, "count": count} for company, count in hot_companies]

    return Response({
        "total": total, 
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "results": jobs,
        "city_options": city_options,
        "education_options": education_options,
        "experience_level_options": experience_level_options,
        "hot_jobs": hot_jobs,
        "hot_cities": hot_cities,
        "hot_companies": hot_companies,
        })

@api_view(["GET"])
@permission_classes([AllowAny])
def job_detail(request, job_id):
    """
    岗位详情 API
    参数：
      - job_id: 岗位ID（路径参数）
    返回：
      - job_id: 岗位ID
      - title: 岗位标题
      - company_name: 公司名称
      - salary: 薪资
      - month_salary_avg: 平均月薪资
      - location_city: 城市
      - education: 学历
      - experience: 经验
      - experience_level: 经验等级
      - recruit_count: 招聘人数
      - recruit_count_parsed: 招聘人数解析后的整数
      - company_industry: 公司行业
      - company_scale: 公司规模
      - company_link: 公司链接
      - has_weekend_off: 是否有周末休息
      - job_url: 岗位链接
      - company_tags: 公司标签
      - job_description: 岗位描述
      - language_requirement: 语言要求
      - update_time_parsed: 更新时间解析后的日期对象

      - company_stats: 公司统计信息
        - job_count: 岗位数量
        - recruit_total: 招聘人数
        - avg_salary: 平均薪资

      - similar_jobs: 相似岗位列表
        - id: 岗位ID
        - title: 岗位标题
        - company_name: 公司名称
        - location_city: 城市
        - salary: 薪资

      - salary_analysis: 薪资分析信息
        - industry_avg: 行业平均薪资
        - above_percentage: 高于行业平均薪资比例
        - range_min: 薪资范围最小值
        - range_max: 薪资范围最大值
    """
    
    # 查询岗位详情
    job = Job.objects.get(id=job_id)

    # —— 岗位详情 ——
    job_data = {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "salary": job.salary,
        "month_salary_avg": job.month_salary_avg,
        "location_city": job.location_city,
        "education": job.education,
        "experience": job.experience,
        "experience_level": job.experience_level,
        "recruit_count": job.recruit_count,
        "recruit_count_parsed": job.recruit_count_parsed,
        "company_industry": job.company_industry,
        "company_scale": job.company_scale,
        "company_link": job.company_link,
        "has_weekend_off": job.has_weekend_off,
        "job_url": job.job_url,
        "company_tags": job.company_tags if isinstance(job.company_tags, list) else [],
        "job_description": job.job_description,
        "language_requirement": job.language_requirement,
        "update_time_parsed": job.update_time_parsed.strftime("%Y-%m-%d") if job.update_time_parsed else None,
    }

    # —— 公司统计信息 ——
    company_stats = {}
    # 查询公司下所有岗位
    company_jobs_qs = Job.objects.filter(company_name=job.company_name)
    # 统计岗位数量
    company_job_count = company_jobs_qs.count()
    # 统计招聘人数
    company_recruit_total = company_jobs_qs.aggregate(
        total=Sum("recruit_count_parsed")
    )["total"] or 0
    # 统计平均薪资
    company_avg_salary = company_jobs_qs.aggregate(
        avg=Avg("month_salary_avg")
    )["avg"] or 0
    # 返回公司统计信息
    company_stats = {
        "job_count": company_job_count,
        "recruit_total": company_recruit_total,
        "avg_salary": round(company_avg_salary, 0),
    }

    # —— 相似岗位推荐列表（可插拔推荐系统） ——
    # 调用推荐引擎获取相似岗位
    similar_jobs = recommend(job, top_k=5)

    # —— 薪资分析信息 ——
    # 查询行业下所有岗位
    industry_jobs_qs = Job.objects.filter(company_industry=job.company_industry)
    industry_total = industry_jobs_qs.count()
    # 行业平均薪资
    industry_avg = industry_jobs_qs.aggregate(avg=Avg("month_salary_avg"))["avg"] or 0
    # 当前薪资高于行业平均薪资的比例（空值则按0处理）
    above_percentage = round((job.month_salary_avg - industry_avg) / industry_avg * 100, 1) if industry_avg > 0 and job.month_salary_avg else 0.0
    # 行业薪资范围
    salary_range = industry_jobs_qs.aggregate(
        range_min=Min("month_salary_avg"),
        range_max=Max("month_salary_avg"),
    )
    salary_analysis = {
        "industry_avg": round(industry_avg, 0),
        "above_percentage": above_percentage,
        "range_min": salary_range["range_min"] or 0,
        "range_max": salary_range["range_max"] or 0,
    }

    return Response({
        **job_data,     # **代表展开字典，将键值对直接添加到响应中
        "company_stats": company_stats,
        "similar_jobs": similar_jobs,
        "salary_analysis": salary_analysis,
        })

@api_view(["GET"])
@permission_classes([AllowAny])
def salary_analysis(request):
    """
    薪资分析 API
    参数：
    - category: 岗位类别
    - location_partition: 城市分区
    返回：
    - stats: 统计信息
    - salary_range_distribution: 薪资区间分布
    - city_salary_ranking: 城市薪资排名
    - industry_salary_ranking: 行业薪资排名
    - scale_salary: 公司规模与薪资关系
    - education_salary: 学历与薪资关系
    - experience_salary: 经验与薪资关系
    - category_boxplot: 岗位类别与薪资关系
    """

    # 获取岗位类别（逗号分隔的多值）
    category_param = request.query_params.get("category", "")
    # 获取城市分区（逗号分隔的多值）
    partition_param = request.query_params.get("location_partition", "")

    # 获取全量数据
    base_queryset = Job.objects.all()
    # 筛选数据
    queryset = base_queryset

    if category_param:
        categories = [c.strip() for c in category_param.split(",") if c.strip()]
        if categories:
            queryset = queryset.filter(category__in=categories)
    if partition_param:
        partitions = [p.strip() for p in partition_param.split(",") if p.strip()]
        if partitions:
            queryset = queryset.filter(location_partition__in=partitions)

    job_data = list(queryset.values("id", "month_salary_avg", "location_city", "company_industry", "company_scale", "education", "experience_level", "category"))

    # —— 统计信息 ——
    stats = {}
    agg_res = queryset.aggregate(avg=Avg("month_salary_avg"), max=Max("month_salary_avg"))
    avg_salary = agg_res["avg"] or 0
    max_salary = agg_res["max"] or 0
    salary_arr = [s for job in job_data if (s := job["month_salary_avg"]) is not None]  # 海象运算符，少一次字典索引
    # 计算中位数
    median_salary = median(salary_arr) if salary_arr else 0

    stats["avg_salary"] = round(avg_salary, 0)
    stats["max_salary"] = round(max_salary, 0)
    stats["median_salary"] = round(median_salary, 0)

    # —— 薪资区间分布 ——
    salary_range_distribution_dict = {
    "0-10k": 0,
    "10k-20k": 0,
    "20k-30k": 0,
    "30k-50k": 0,
    "50k+": 0
    }
    for job in job_data:
        salary = job["month_salary_avg"]
        if salary is None:
            continue
        if 0 < salary <= 10000:
            salary_range_distribution_dict["0-10k"] += 1
        elif 10000 < salary <= 20000:
            salary_range_distribution_dict["10k-20k"] += 1
        elif 20000 < salary <= 30000:
            salary_range_distribution_dict["20k-30k"] += 1
        elif 30000 < salary <= 50000:
            salary_range_distribution_dict["30k-50k"] += 1
        elif salary > 50000:
            salary_range_distribution_dict["50k+"] += 1

    salary_range_distribution = [{"range": k, "count": v} for k, v in salary_range_distribution_dict.items()]
        
    # —— 城市薪资排名 ——
    city_salary_ranking_dict = queryset.order_by().values("location_city").annotate(avg=Avg("month_salary_avg")).order_by("-avg")
    city_salary_ranking = [{"city": item["location_city"], "avg_salary": round(item["avg"] or 0)} for item in city_salary_ranking_dict]

    # —— 行业薪资排名 ——
    industry_salary_ranking_dict = queryset.order_by().values("company_industry").annotate(avg=Avg("month_salary_avg")).order_by("-avg")
    industry_salary_ranking = [{"industry": item["company_industry"], "avg_salary": round(item["avg"] or 0)} for item in industry_salary_ranking_dict]

    # —— 公司规模与薪资关系 ——
    scale_salary_dict = queryset.order_by().values("company_scale").annotate(avg=Avg("month_salary_avg")).order_by("-avg")
    scale_salary = [{"scale": item["company_scale"], "avg_salary": round(item["avg"] or 0)} for item in scale_salary_dict]

    # —— 学历与薪资关系 ——
    education_salary_dict = queryset.order_by().values("education").annotate(avg=Avg("month_salary_avg")).order_by("-avg")
    education_salary = [{"education": item["education"], "avg_salary": round(item["avg"] or 0)} for item in education_salary_dict]

    # —— 经验与薪资关系 ——
    experience_salary_dict = queryset.order_by().values("experience_level").annotate(avg=Avg("month_salary_avg")).order_by("-avg")
    experience_salary = [{"experience_level": item["experience_level"], "avg_salary": round(item["avg"] or 0)} for item in experience_salary_dict]

    # —— 岗位类别与薪资关系 ——
    # 计算各类别的min，q1，median，q3，max
    all_data = pd.DataFrame(base_queryset.values("category", "month_salary_avg"))
    all_data = all_data.dropna(subset=["month_salary_avg"])  # 移除空值
    all_data["month_salary_avg"] = all_data["month_salary_avg"] / 1000  # 统一转为K单位
    category_boxplot = []
    for category, group in all_data.groupby("category"):
        salary_series = group["month_salary_avg"]
        category_boxplot.append({
            "category": category,
            "min": round(salary_series.min(), 0),
            "q1": round(salary_series.quantile(0.25), 0),
            "median": round(salary_series.median(), 0),
            "q3": round(salary_series.quantile(0.75), 0),
            "max": round(salary_series.max(), 0),
        })

    # 解决中文+负号乱码（必须在 sns.set_style 之后设置，否则会被覆盖）
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False

    # —— 周末双休与薪资关系 ——
    # 绘制分组堆叠柱状图
    all_data_weekend_off = pd.DataFrame(queryset.values("has_weekend_off", "month_salary_avg")).dropna(subset=["month_salary_avg"])
    all_data_weekend_off["month_salary_avg"] = all_data_weekend_off["month_salary_avg"] / 1000

    # 画布尺寸、整体风格
    plt.figure(figsize=(16,8))
    sns.set_style("whitegrid") # 白底细网格，清爽美观
    # set_style 会重置字体，重新设置
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False

    # 配色：双休#4A90E2(天蓝)、非双休#E67E22(暖橙)，透明度优化
    sns.histplot(
        x="month_salary_avg",
        hue="has_weekend_off",
        data=all_data_weekend_off,
        kde=True,
        palette=["#4A90E2", "#E67E22"],
        alpha=0.65, # 柱状半透明不遮挡
        edgecolor="#ffffff", # 柱子白边框区分
        linewidth=0.8
    )

    # 标题、坐标轴美化
    plt.title("周末双休 vs 非双休岗位薪资分布", fontsize=32, pad=18)
    plt.xlabel("月薪（K）", fontsize=24, labelpad=18)
    plt.ylabel("岗位数量", fontsize=24, labelpad=18)
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)

    # 图例美化（位置右上、去掉边框）
    leg = plt.legend(["周末双休", "非周末双休"], loc="upper right", frameon=False, fontsize=20)

    # 去掉顶部、右侧多余边框
    sns.despine(top=True, right=True)
    plt.tight_layout()

    # 后续base64生成图片代码不变
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    weekend_off_salary_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    weekend_off_salary_image = f"data:image/png;base64,{weekend_off_salary_image}"
    plt.close()  # 必须关闭，防止内存泄漏

    # —— 外语要求与薪资关系 ——
    # 绘制分组堆叠柱状图
    all_data_language = pd.DataFrame(queryset.values("has_language_requirement", "month_salary_avg")).dropna(subset=["month_salary_avg"])
    all_data_language["month_salary_avg"] = all_data_language["month_salary_avg"] / 1000    

    # 画布尺寸、整体风格
    plt.figure(figsize=(16,8))
    sns.set_style("whitegrid") # 白底细网格，清爽美观
    # set_style 会重置字体，重新设置
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False

    # 配色：双休#4A90E2(天蓝)、非双休#E67E22(暖橙)，透明度优化
    sns.histplot(
        x="month_salary_avg",
        hue="has_language_requirement",
        data=all_data_language,
        kde=True,
        palette=["#4A90E2", "#E67E22"],
        alpha=0.65, # 柱状半透明不遮挡
        edgecolor="#ffffff", # 柱子白边框区分
        linewidth=0.8
    )

    # 标题、坐标轴美化
    plt.title("外语要求与薪资分布", fontsize=32, pad=18)
    plt.xlabel("月薪（K）", fontsize=24, labelpad=18)
    plt.ylabel("岗位数量", fontsize=24, labelpad=18)
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)

    # 图例美化（位置右上、去掉边框）
    leg = plt.legend(["外语要求", "无外语要求"], loc="upper right", frameon=False, fontsize=20)

    # 去掉顶部、右侧多余边框
    sns.despine(top=True, right=True)
    plt.tight_layout()

    # 后续base64生成图片代码不变
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    language_salary_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    language_salary_image = f"data:image/png;base64,{language_salary_image}"
    plt.close()  # 必须关闭，防止内存泄漏
    
    return Response({
        "stats": stats,
        "salary_range_distribution": salary_range_distribution,
        "city_salary_ranking": city_salary_ranking,
        "industry_salary_ranking": industry_salary_ranking,
        "scale_salary": scale_salary,
        "education_salary": education_salary,
        "experience_salary": experience_salary,
        "weekend_off_boxplot": weekend_off_salary_image,
        "language_boxplot": language_salary_image,
        "category_boxplot": category_boxplot
    })

@api_view(["GET"])
@permission_classes([AllowAny])
def get_dashboard(request):
    """
    获取仪表盘数据 API

    values()：返回字典列表 QuerySet，按指定字段提取多行原始数据，支持分组统计（annotate）
    values_list()：返回元组列表 QuerySet，纯数值 / 字段值，轻量化；flat=True 直接返回一维值列表
    aggregate()：一次性聚合计算，返回单个字典，不返回多行数据，只算总和、均值、总数这类全局指标
    """


    job_count = Job.objects.count()
    company_count = Job.objects.values_list('company_name', flat=True).distinct().count()
    avg_salary = Job.objects.aggregate(avg_salary=Avg('month_salary_avg'))['avg_salary']
    city_count = Job.objects.values_list('location_city', flat=True).distinct().count()

    # 各个岗位类别的岗位数，按数量降序
    category_list = list(
        Job.objects.values('category')
        .annotate(count=Count('category'))
        .order_by('-count')
    )

    return Response({
        "job_count": job_count,
        "company_count": company_count,
        "avg_salary": round(avg_salary) if avg_salary else 0,
        "city_count": city_count,
        "category_list": category_list
    })
