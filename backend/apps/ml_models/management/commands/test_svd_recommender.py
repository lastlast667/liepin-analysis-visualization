from django.core.management.base import BaseCommand
from apps.ml_models.recommenders.svd_recommender import SVDRecommender
from apps.users.models import User

class Command(BaseCommand):
    help = "测试SVD推荐器"
    def handle(self, *args, **options):
        rec = SVDRecommender()

        # 测试已存在用户的推荐
        self.stdout.write("测试已存在用户的推荐:")
        user = User.objects.filter(favorites__isnull=False).first()
        if user:
            job_ids = rec.recommend(user.id, top_k=5)
            self.stdout.write(f"推荐给用户 {user.id} 的岗位ID: {job_ids}")
        
        # 测试新用户的推荐
        self.stdout.write("测试新用户的推荐:")
        new_user = User.objects.filter(favorites__isnull=True, browse_history__isnull=True).first()
        if new_user:
            job_ids = rec.recommend(new_user.id, top_k=5)
            self.stdout.write(f"新用户推荐结果: {job_ids}")