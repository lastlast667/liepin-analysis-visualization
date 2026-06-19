"""
基于类别的推荐

逻辑：同 category 中的岗位中，按月薪接近度排序
"""

from apps.analysis.recommenders.base import BaseRecommender
from apps.jobs.models import Job

class CategoryBasedRecommender(BaseRecommender):
    @property   # 把类方法伪装成属性，调用不用加 ()
    def name(self) -> str:
        return "category_based"
    
    def recommend(self, job, top_k: int = 5) -> list[dict]:
        """
        基于类别的推荐
        """
        # get精准获取一条数据，filter筛选出多条匹配数据
        queryset = Job.objects.filter(category=job.category).exclude(id=job.id)

        scored = []
        for other in queryset:
            score = 0.0 # 初始化分数为 0
            # 薪资接近度：差异越小分越高
            if job.month_salary_avg and other.month_salary_avg:
                max_sal = max(job.month_salary_avg, other.month_salary_avg)
                diff_ratio = abs(job.month_salary_avg - other.month_salary_avg) / max_sal   # abd取绝对值，确保结果为非负
                score = round(100 * (1 - diff_ratio), 1)
            scored.append({"job_id": other.id, "score": score})
        
        # 按分数降序排序，取 top_k 个
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
                
    

