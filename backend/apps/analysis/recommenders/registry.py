"""
推荐源注册中心

管理所有推荐源实例，支持注册和获取。
"""
from apps.analysis.recommenders.base import BaseRecommender

class RecommenderRegistry:
    """推荐源注册中心（全局单例）"""
    _sources: dict[str, BaseRecommender] = {}

    @classmethod    # 类方法，无需实例化，直接类名调用
    def register(cls, recommender: BaseRecommender):
        """注册推荐源"""
        cls._sources[recommender.name] = recommender

    @classmethod
    def get_all(cls) -> list[BaseRecommender]:
        """获取所有注册的推荐源"""
        return list(cls._sources.values())
    
    @classmethod
    def clear(cls):
        """清空所有注册的推荐源（仅用于测试环境）"""
        cls._sources.clear()
