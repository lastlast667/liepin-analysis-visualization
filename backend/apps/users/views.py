from .models import BrowseHistory
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from apps.users.serializers import BrowseHistorySerializer, FavoriteSerializer, UserProfileSerializer

from .models import Favorite, User, UserProfile


def test_view(request):
    return Response({"status": "ok", "message": "No CSRF check!"})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """用户登录"""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "请输入用户名和密码"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"detail": "用户名或密码错误"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "token": token.key,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    })


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """用户注册"""
    username = request.data.get("username")
    email = request.data.get("email", "")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "用户名和密码不能为空"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 6:
        return Response(
            {"detail": "密码长度至少为6位"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "用户名已存在"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(["POST"])
def logout_view(request):
    """用户登出"""
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
    except (Token.DoesNotExist, AttributeError):
        pass
    logout(request)
    return Response({"detail": "已登出"})


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """获取/更新当前用户信息"""
    user = request.user
    if request.method == "GET":
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })
    # PUT
    data = request.data
    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    user.save()
    return Response({"detail": "用户信息更新成功"}, status=status.HTTP_200_OK)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])  # 仅登录用户才能访问
def favorites(request):
    """用户收藏列表"""
    user = request.user # 当前登录用户
    if request.method == "GET":
        favorites_qs = user.favorites.select_related("job").all()   # 自带隐式过滤条件，只查询当前登录用户的收藏记录
                                                                    # select_related("job") 代表外键联表 JOIN 查询
        serializer = FavoriteSerializer(favorites_qs, many=True)    # 将查出来的 QuerySet 转换为 JSON 格式
        return Response(serializer.data)    # 前端期望的是数组，所以直接返回 serializer.data

    # POST - 添加收藏
    data = request.data
    job_id = data.get("job_id")
    if not job_id:
        return Response(
            {"detail": "请提供岗位ID"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    favorite, created = Favorite.objects.get_or_create(user=user, job_id=job_id)
    if not created:
        return Response({"detail": "已收藏过该岗位"}, status=400)

    serializer = FavoriteSerializer(favorite)
    return Response(serializer.data, status=201)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def favorite_delete(request, id):
    """取消收藏岗位"""
    user = request.user
    deleted, _ = user.favorites.filter(id=id).delete()  # _ 忽略返回值
    if not deleted:
        return Response(
            {"detail": "收藏岗位不存在"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response({"detail": "已取消收藏"}, status=status.HTTP_200_OK)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def browse_history(request):
    """用户浏览历史"""
    user = request.user
    if request.method == "GET":
        history_qs = user.browse_history.select_related("job").all()
        serializer = BrowseHistorySerializer(history_qs, many=True)
        return Response(serializer.data)
    
    # POST - 添加浏览历史
    data = request.data
    job_id = data.get("job_id") # 从请求体中获取岗位ID，需要看前端代码中的请求体格式
    if not job_id:
        return Response(
            {"detail": "请提供岗位ID"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    BrowseHistory.objects.update_or_create(user=user, job_id=job_id)  # update_or_create 方法，更新或创建新记录
    return Response({"detail": "已记录浏览历史"}, status=201)

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    """获取/更新个人资料"""
    user = request.user
    profile_instance, _ = UserProfile.objects.get_or_create(user=user)  # .get_or_create() 方法是 QuerySet 方法，返回一个元组，第一个元素是查询到的实例，第二个元素是是否创建了新实例

    if request.method == "GET":
        return Response({
            "username":user.username,   # 或者写成 profile_instance.user.username
            "email":user.email,
            "expected_city":profile_instance.expected_city,
            "expected_category":profile_instance.expected_category,
            "skills":profile_instance.skills,
            "resume_text":profile_instance.resume_text,
        })
    
    # PUT
    data = request.data
    if "expected_city" in data:
        profile_instance.expected_city = data["expected_city"]
    if "expected_category" in data:
        profile_instance.expected_category = data["expected_category"]
    if "skills" in data:
        profile_instance.skills = data["skills"]
    if "resume_text" in data:
        profile_instance.resume_text = data["resume_text"]
    profile_instance.save() # 把内存修改持久化到数据库
    return Response({"detail": "个人资料更新成功"}, status=status.HTTP_200_OK)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_password(request):
    """更新密码"""
    user = request.user
    data = request.data
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not user.check_password(old_password):   # 继承自 AbstractUser 模型的 check_password 方法
        return Response(
            {"detail": "旧密码错误"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    if len(new_password) < 6:
        return Response(
            {"detail": "密码长度至少为6位"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    user.set_password(new_password)
    user.save()
    return Response({"detail": "密码更新成功"}, status=status.HTTP_200_OK)
