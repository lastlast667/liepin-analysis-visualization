"""
初始化 MLModel 表数据
用法： python manage.py init_ml_models
"""
from django.core.management.base import BaseCommand
from apps.ml_models.models import MLModel
import pickle
from job_analysis.app_config import MODEL_DIR



class Command(BaseCommand):
    help = "初始化 MLModel 表数据"

    def handle(self, *args, **options):
        # 从训练好的元数据中读取真实 R2
        salary_accuracy = None
        try:
            with open(MODEL_DIR / "salary_predict_meta.pkl", "rb") as f:
                salary_meta = pickle.load(f)
            if salary_meta.get('r2') is not None:
                salary_accuracy = round(salary_meta.get('r2'), 4)
        except FileNotFoundError:
            pass

        models_data = [
            {"name": "薪资预测器", "model_type": "salary_predictor", "accuracy": salary_accuracy, "is_active": True},
            {"name": "推荐模型", "model_type": "recommender", "is_active": True},
            {"name": "简历匹配器", "model_type": "resume_matcher", "is_active": True},
        ]

        for data in models_data:
            obj, created = MLModel.objects.update_or_create(   # update_or_create 方法固定返回一个二元元组 (tuple)，第一个元素是模型实例，第二个元素是布尔类型。
                model_type=data["model_type"],
                defaults=data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ 已更新: {data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"已存在: {data['name']}"))

        self.stdout.write(self.style.SUCCESS("MLModel 初始化完成"))