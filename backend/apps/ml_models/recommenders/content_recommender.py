"""
基于内容的推荐器
"""
from apps.analysis.recommenders.base import BaseRecommender
from apps.jobs.models import Job
from apps.users.models import UserProfile

class ContentRecommender(BaseRecommender):
    @property
    def name(self) -> str:
        return "基于内容推荐"
    
    def recommend(self, user_id, top_k=20, **kwargs):
        """
        推荐用户 user_id 的 top_k 个岗位
        """
        # 1. 获取用户画像
        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return []
        except Exception as e:
            print(f"推荐器 {self.name} 推荐用户 {user_id} 时出错: {e}")
            return []
        
        expected_city = profile.expected_city or ""
        expected_category = profile.expected_category or ""

        # 2. 如果用户没设置任何偏好，没法推荐
        if not expected_city and not expected_category:
            return []
        
        # 3. 筛选岗位
        jobs = Job.objects.all()
        if expected_city:
            # 把逗号分隔的多个城市拆开匹配
            cities = expected_city.split(",")
            jobs = jobs.filter(location_city__in=cities)
        if expected_category:
            # 把逗号分隔的多个分类拆开匹配
            categories = expected_category.split(",")
            jobs = jobs.filter(category__in=categories)

        # 4. 打分：城市+类别都匹配 = 100 分，仅类别匹配 = 70 分，仅城市匹配 = 50 分，其他 = 0 分
        scored = []
        for job in jobs:
            score = 0
            if job.location_city in cities and job.category in categories:
                score = 100
            elif job.category in categories:
                score = 70
            elif job.location_city in cities:
                score = 50
            else:
                score = 0
            scored.append({"job_id": job.id, "score": score})

        # 5. 排序，按分数从高到低，取前 top_k 个岗位
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

