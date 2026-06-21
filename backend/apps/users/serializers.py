"""
安装插件：pip install djangorestframework-camel-case
"""
from rest_framework import serializers
from .models import User, Favorite, UserProfile, BrowseHistory
from apps.jobs.models import Job

class JobBriefSerializer(serializers.ModelSerializer):
    """岗位简要信息序列化器（嵌套用）"""
    match_score = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ["id", "title", "company_name", "salary",
                  "location_city", "experience", "education", 
                  "company_industry", "company_scale", "recruit_count",
                  "match_score"]

    def get_match_score(self, obj):
        # DRF 自动循环每一条岗位 obj，触发 get_match_score 方法，把返回值塞进 JSON 的 match_score 字段
        score_map = self.context.get("score_map", {})   # self.context是实例属性
        return score_map.get(obj.id)  # 没有 context 时返回 None，前端 v-if 隐藏

class FavoriteSerializer(serializers.ModelSerializer):
    """收藏列表序列化器"""
    job = JobBriefSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "job", "created_at"]

class BrowseHistorySerializer(serializers.ModelSerializer):
    """浏览历史序列化器"""
    job = JobBriefSerializer(read_only=True)  # 嵌套展开，把整条 Job 岗位完整信息嵌套进收藏记录

    class Meta:
        model = BrowseHistory
        fields = ["id", "job", "browse_time"]   # 写models.py中的属性名而非数据库列名

class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器"""
    class Meta:
        model = UserProfile
        fields = ["user", "expected_city", "expected_category", "skills", "resume_text"]


        