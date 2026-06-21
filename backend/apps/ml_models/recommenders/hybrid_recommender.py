"""
混合推荐器
"""

from apps.analysis.recommenders.base import BaseRecommender
from apps.ml_models.recommenders.svd_recommender import SVDRecommender
from apps.ml_models.recommenders.content_recommender import ContentRecommender
from apps.users.models import User

class HybridRecommender(BaseRecommender):
    @property
    def name(self) -> str:
        return "混合推荐"
    
    def recommend(self, user_id: int, top_k: int = 20) -> list[dict]:
        """
        混合推荐
        """
        # 1. 调用两个推荐器
        svd = SVDRecommender()
        content = ContentRecommender()

        svd_scores = svd.recommend(user_id, top_k=top_k)
        content_scores = content.recommend(user_id, top_k=top_k)

        # 2. 合并加权：对每个出现的岗位，算 60% SVD + 40% 内容
        score_map = {}
        for item in svd_scores:
            score_map[item["job_id"]] = score_map.get(item["job_id"], 0) + item["score"] * 0.60
        for item in content_scores:
            score_map[item["job_id"]] = score_map.get(item["job_id"], 0) + item["score"] * 0.40       
        
        # 3. 按分数降序排序，取 top_k 个
        scored = [{"job_id": job_id, "score": score} for job_id, score in score_map.items()]
        scored.sort(key=lambda x: x["score"], reverse=True)

        return scored[:top_k]
