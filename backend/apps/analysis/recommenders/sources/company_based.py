"""
基于 公司规模 + 公司行业 的推荐

逻辑：同 company 中的岗位中，按月薪接近度排序
"""
from apps.analysis.recommenders.base import BaseRecommender
from apps.jobs.models import Job
from django.db.models import Q

class CompanyBasedRecommender(BaseRecommender):
    @property
    def name(self) -> str:
        return "company_based"
    
    def recommend(self, job, top_k: int = 5) -> list[dict]:
        """
        基于 公司规模 + 公司行业 的推荐
        """
        queryset = Job.objects.filter(Q(company_scale=job.company_scale) | Q(company_industry=job.company_industry)).exclude(id=job.id)

        scored = []
        for other in queryset:
            score = 0.0
            if job.month_salary_avg and other.month_salary_avg:
                max_sal = max(job.month_salary_avg, other.month_salary_avg)
                diff_ratio = abs(job.month_salary_avg - other.month_salary_avg) / max_sal   # abd取绝对值，确保结果为非零
                score = round(100 * (1 - diff_ratio), 1)
                if other.company_scale == job.company_scale:
                    score += 10
                if other.company_industry == job.company_industry:
                    score += 10
            scored.append({"job_id": other.id, "score": score})
        
        # 按分数降序排序，取 top_k 个
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]