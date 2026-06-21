"""
SVD推荐器
"""
import numpy as np

from apps.analysis.recommenders.base import BaseRecommender
from job_analysis.app_config import MODEL_DIR
import pickle


class SVDRecommender(BaseRecommender):
    @property
    def name(self):
        return "SVD推荐器"
    
    def __init__(self):
        self._model = None

    @property
    def model(self):
        """
        机器学习算法的模型不同于普通推荐器的模型，需要从文件加载加载模型
        模型中包含用户-岗位矩阵、岗位-岗位矩阵、岗位-岗位矩阵的奇异值
        """
        if self._model is None:
            with open(MODEL_DIR / "svd_model.pkl", "rb") as f:
                self._model = pickle.load(f)
        return self._model

    def recommend(self, user_id, top_k=20, **kwargs):
        """
        推荐用户 user_id 的 top_k 个岗位
        普通推荐器需要从请求中获取数据（job_id），机器学习推荐器直接从训练好的模型中获取用户-岗位矩阵和岗位-岗位矩阵的奇异值
        """
        # 1. 冷启动：新用户无隐向量，返回空列表
        model = self.model
        if user_id not in model['user_idx']:
            return []
        
        # 2. 计算所有岗位的预测评分
        user_idx = model['user_idx'][user_id]
        user_vec = model['U'][user_idx]
        # job_vecs = diag(sigma) @ Vt   #所有岗位向量
        scores = (user_vec * model['sigma']) @ model['Vt']  # 单用户全岗位评分

        # 3. 排序并返回 top_k 个岗位
        top_indices = np.argsort(scores)[::-1][:top_k]  # 从高到低排序，取前 top_k 个，存放的是矩阵列号
        scored = [{"job_id": model['job_ids'][idx], "score": scores[idx]} for idx in top_indices]
        return scored
        
        

        
