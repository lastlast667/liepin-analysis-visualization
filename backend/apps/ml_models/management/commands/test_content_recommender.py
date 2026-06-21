from django.core.management.base import BaseCommand
from apps.ml_models.recommenders.content_recommender import ContentRecommender
from apps.users.models import User
from apps.analysis.recommenders.registry import RecommenderRegistry



class Command(BaseCommand):
    help = "测试内容推荐器"

    def add_arguments(self, parser):
        parser.add_argument("--user_id", type=int, default=1, help="用户ID，用于测试")

    def handle(self, *args, **options):
        user_id = options["user_id"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stderr.write(f"用户 {user_id} 不存在")
            return
        
        rec = ContentRecommender()
        result = rec.recommend(user_id, top_k=5)
        self.stdout.write(f"推荐给用户 {user_id} 的岗位ID: {result}")
        self.stdout.write(f"共返回 {len(result)} 条")
        


        
