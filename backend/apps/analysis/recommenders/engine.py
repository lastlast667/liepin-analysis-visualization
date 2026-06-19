"""
聚合引擎

从注册中心获取所有推荐源，聚合各源得分，加权排序后返回
"""
from apps.analysis.recommenders.registry import RecommenderRegistry
from apps.jobs.models import Job
from apps.analysis.recommenders.sources.category_based import CategoryBasedRecommender
from apps.analysis.recommenders.sources.company_based import CompanyBasedRecommender
from apps.analysis.recommenders.sources.rule_based import RuleBasedRecommender

def _register_sources():
    """
    惰性注册所有推荐源
    """
    if not RecommenderRegistry.get_all():
        RecommenderRegistry.register(CategoryBasedRecommender())
        RecommenderRegistry.register(CompanyBasedRecommender())
        RecommenderRegistry.register(RuleBasedRecommender())

def recommend(job, top_k: int = 5) -> list[dict]:
    """
    推荐函数
    :param Job: 输入岗位
    :param top_k: 返回推荐岗位数量
    :return: :return: [
        {"id": 1, "title": "...", "company_name": "...", "location_city": "...", "salary": "...", "match_score": 95, ...},
        ...
    ]
    """
    _register_sources() # 确保已注册
    
    # 1. 遍历所有推荐源，汇总得分
    all_scores = {} # {job_id: score}
    for source in RecommenderRegistry.get_all():
        results = source.recommend(job=job, top_k=top_k)
        for result in results:
            job_id = result["job_id"]
            all_scores[job_id] = all_scores.get(job_id, 0.0) + result["score"]

    # 2. 按总分降序排序
    sorted_scores = sorted(all_scores.items(), key=lambda x: all_scores[x[0]], reverse=True)[:top_k]

    # 3. 查 DB 组装完整字段返回
    similar_jobs = []
    for job_id, score in sorted_scores:
        similar_job = Job.objects.get(id=job_id)
        similar_jobs.append({
            "id": similar_job.id,
            "title": similar_job.title,
            "company_name": similar_job.company_name,
            "location_city": similar_job.location_city,
            "salary": similar_job.salary,
        })
    
    return similar_jobs