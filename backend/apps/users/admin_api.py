"""
管理员接口

数据统计、用户列表、删除用户、岗位列表、删除岗位
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from apps.jobs.models import Job
from apps.users.models import User, Favorite, BrowseHistory
from django.db.models import Count



@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_stats(request):
    """数据统计"""
    return Response({
        "total_users": User.objects.count(),
        "total_jobs": Job.objects.count(),
        "total_favorites": Favorite.objects.count(),
        "total_browse": BrowseHistory.objects.count(),
        "category_status": list(Job.objects.values("category")
            .annotate(count=Count("id")).order_by("-count")[:10]),
        })

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_users(request):
    """用户列表"""
    users = User.objects.all().values("id", "username", "email", "phone", 
        "is_staff", "is_active")
    return Response(list(users))

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_user_delete(request, id):
    """删除用户"""
    User.objects.get(id=id).delete()
    return Response({"detail": "用户删除成功"})
    
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_jobs(request):
    """岗位列表"""
    jobs = Job.objects.all().values("id", "title", "company_name", 
        "location_city", "category", "salary")
    return Response(list(jobs))
    
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_job_delete(request, id):
    """删除岗位"""
    Job.objects.get(id=id).delete()
    return Response({"detail": "岗位删除成功"})
    