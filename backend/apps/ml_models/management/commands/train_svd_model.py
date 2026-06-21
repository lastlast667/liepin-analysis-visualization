from scipy.sparse import csr_matrix
"""
训练SVD模型
"""
import pickle
from django.core.management.base import BaseCommand
import numpy as np
from sklearn.decomposition import TruncatedSVD
from apps.jobs.models import Job
from apps.users.models import User, BrowseHistory, Favorite
from scipy.sparse.linalg import svds

from job_analysis.app_config import MODEL_DIR
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_svd_model")



class Command(BaseCommand):
    """
    训练SVD模型
    """
    help = "训练SVD模型"
    
    def handle(self, *args, **options):
        """
        处理命令逻辑
        """
        # 1. 构建 User * Job 评分矩阵
        users = list(User.objects.all())
        jobs = list(Job.objects.all())
        user_idx = {user.id: idx for idx, user in enumerate(users)}
        job_idx = {job.id: idx for idx, job in enumerate(jobs)}

        R = np.zeros((len(users), len(jobs)))   # 用户 * 岗位 评分矩阵
        
        # 浏览历史 +1/次
        for bh in BrowseHistory.objects.all():
            if bh.user.id in user_idx and bh.job.id in job_idx:
                R[user_idx[bh.user.id], job_idx[bh.job.id]] += 1
        
        # 收藏 +3/次
        for favorite in Favorite.objects.all():
            if favorite.user.id in user_idx and favorite.job.id in job_idx:
                R[user_idx[favorite.user.id], job_idx[favorite.job.id]] += 3

        # 2. SVD分解（k=50 个隐因子）
        k = min(50, min(len(users), len(jobs)) - 1) # k维压缩
        U, sigma, Vt = svds(csr_matrix(R), k=k) # 把稠密的 0 矩阵 R 转成稀疏矩阵

        # 3. 保存模型
        model_data = {
            "U": U,                                 # (n_users, k)
            "Vt": Vt,                               # (k, n_jobs)
            "sigma": sigma,                         # (k,)
            "user_idx": user_idx,                   # {user_id: idx} 用户ID -> 矩阵行号
            "job_idx": job_idx,                     # {job_id: idx} 岗位ID -> 矩阵列号
            "job_ids": [job.id for job in jobs],    # 矩阵列号 -> 岗位ID（逆映射）
        }

        with open(MODEL_DIR / "svd_model.pkl", "wb") as f:
            pickle.dump(model_data, f)
        logger.info("SVD模型训练完成并保存")
