"""
推荐系统基类

所有推荐源必须继承 BaseRecommender 并实现 recommend() 方法
"""

from abc import ABC, abstractmethod


class BaseRecommender(ABC):
    """推荐源基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """推荐源名称（唯一标识，用于注册中心和调试）"""
        return self.__class__.__name__
    
    # @abstractmethod 保证了任何继承这个类的子类，如果不实现 recommend() 方法，实例化时会直接报错。
    @abstractmethod
    def recommend(self, job, top_k = 5) -> list[dict]:
        """
        根据当前岗位推荐相似岗位

        :param job: 当前岗位信息
        :param top_k: 推荐岗位数量，默认5个
        :return: [{"job_id": int, "score": float}, ...]
                 score 越高表示越相似，范围 0~100
        """
        
