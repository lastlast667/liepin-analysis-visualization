from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import User


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """获取当前用户信息"""
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })
