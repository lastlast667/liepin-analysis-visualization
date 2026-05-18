from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from apps.jobs.models import Job
from apps.users.models import User
from apps.spider.models import SpiderTask
from apps.ml_models.models import MLModel
from apps.ai_chat.models import ChatMessage


@method_decorator(staff_member_required, name="dispatch")
class DashboardView(View):
    template_name = "admin/dashboard.html"

    def get(self, request):
        total_jobs = Job.objects.count()
        total_users = User.objects.count()
        active_models = MLModel.objects.filter(is_active=True).count()
        today_jobs = Job.objects.filter(created_at__date=Job.objects.datetimes("created_at", "day").last()).count()
        latest_tasks = SpiderTask.objects.order_by("-started_at")[:5]
        category_stats = Job.objects.values("category").annotate(count=Count("id")).order_by("-count")[:10]

        data = {
            "total_jobs": total_jobs,
            "total_users": total_users,
            "active_models": active_models,
            "today_jobs": today_jobs,
            "latest_tasks": latest_tasks,
            "category_stats": category_stats,
        }
        return render(request, self.template_name, data)


@method_decorator(staff_member_required, name="dispatch")
class SpiderControlView(View):
    template_name = "admin/spider_control.html"

    def get(self, request):
        last_task = SpiderTask.objects.order_by("-started_at").first()
        status = "running" if SpiderTask.objects.filter(status="running").exists() else "idle"
        data = {
            "status": status,
            "last_task": last_task,
        }
        return render(request, self.template_name, data)
