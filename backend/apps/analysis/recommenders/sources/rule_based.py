"""
基于同城市+同薪资范围的推荐

逻辑：同城市 + 薪资在 ±20% 范围内
"""
from apps.analysis.recommenders.base import BaseRecommender
from apps.jobs.models import Job
from django.db.models import Q

class RuleBasedRecommender(BaseRecommender):
    @property
    def name(self) -> str:
        return "rule_based"
    
    def recommend(self, job, top_k: int = 5) -> list[dict]:
        """
        基于规则的推荐
        同城市基础分/同省份基础分 + 薪资在 ±20% 范围内奖励分
        """
        # 计算薪资上下限
        # if job.month_salary_avg:
        #     salary_min = job.month_salary_avg * 0.8
        #     salary_max = job.month_salary_avg * 1.2
        # else:
        #     salary_min = 0.0
        #     salary_max = 999999
        
        queryset = Job.objects.filter(Q(location_city=job.location_city) | Q(location_province=job.location_province)).exclude(id=job.id)

        scored = []
        for other in queryset:
            if job.location_city == other.location_city:
                base = 80.0 # 同城市基础分
            elif job.location_province == other.location_province:
                base = 60.0 # 同省份基础分
            
            if job.month_salary_avg and other.month_salary_avg:
                max_sal = max(job.month_salary_avg, other.month_salary_avg)
                diff_ratio = abs(job.month_salary_avg - other.month_salary_avg) / max_sal
                bonus = round(20 * (1 - diff_ratio), 1)
            else:
                bonus = 0.0 # 无薪资信息，不计算奖励

            scored.append({"job_id": other.id,"score": base + bonus})
        
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

        
