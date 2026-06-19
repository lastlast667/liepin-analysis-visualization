"""
测试推荐器

用法：python manage.py test_recommenders --job-id=42
"""
from django.core.management.base import BaseCommand
from apps.analysis.recommenders.registry import RecommenderRegistry
from apps.analysis.recommenders.sources.category_based import CategoryBasedRecommender
from apps.analysis.recommenders.sources.rule_based import RuleBasedRecommender
from apps.analysis.recommenders.sources.company_based import CompanyBasedRecommender
from apps.jobs.models import Job

class Command(BaseCommand):
    help = "测试推荐器"

    def add_arguments(self, parser):
        parser.add_argument("--job-id", type=int, required=True)

    def handle(self, *args, **options):
        job_id = options["job_id"]  # argparse 会自动把横线转成下划线
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            self.stderr.write(f"岗位 {job_id} 不存在")
            return
        
        # 注册所有推荐器
        RecommenderRegistry.clear()
        RecommenderRegistry.register(CategoryBasedRecommender())
        RecommenderRegistry.register(RuleBasedRecommender())
        RecommenderRegistry.register(CompanyBasedRecommender())

        self.stdout.write(f"\n====== 当前岗位：{job.title} （ID={job.id}）======")
        self.stdout.write(f"类别：{job.category}")
        self.stdout.write(f"城市：{job.location_city}")
        self.stdout.write(f"省份：{job.location_province}")
        self.stdout.write(f"月薪：{job.month_salary_avg}")

        for source in RecommenderRegistry.get_all():
            self.stdout.write(f"--- {source.name} ---")
            results = source.recommend(job, top_k=5)
            if not results:
                self.stdout.write("没有推荐岗位")
            else:
                for result in results:
                    other = Job.objects.get(id=result['job_id'])
                    self.stdout.write(f"{result['score']} {other.title} {other.category} {other.location_city} {other.month_salary_avg}")
            self.stdout.write("\n")


        
