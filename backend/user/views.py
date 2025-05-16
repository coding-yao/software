from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from core.permissions import IsAdminUser, IsApproved
from .models import User, Fisher


def generate_token_for_user(user):
    refresh = RefreshToken()
    refresh['account'] = user.user_id
    refresh['role'] = user.role
    return refresh


# 用户注册
@api_view(['POST'])
def register_user(request):
    data = request.data
    account = data.get('account')
    password = data.get('password')
    role = data.get('role', 'user')

    # 检查参数
    if not account:
        return Response({'error': 'missing account'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(account=account).exists():
        return Response({'error': 'account already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({'error': 'missing password'}, status=status.HTTP_400_BAD_REQUEST)

    # 创建用户
    user = User.objects.create(
        account=account,
        password=make_password(password),
        is_approved=False,
        role=role
    )

    # 生成token
    token = generate_token_for_user(user)

    return Response({
        'status': 'success',
        'message': 'register success',
        'user': {
            'user_id': user.user_id,
            'account': user.account,
            'role': user.role
        },
        'access': str(token.access_token),
        'refresh': str(token),
    }, status=status.HTTP_201_CREATED)


# 用户登录
@api_view(['POST'])
def login_user(request):
    account = request.data.get('account')
    password = request.data.get('password')

    # 检查参数缺失
    if not account or not password:
        return Response({'error': 'missing user_id or password'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查用户是否已经注册
    try:
        user = User.objects.get(account=account)
    except User.DoesNotExist:
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查用户账号是否通过注册
    if not user.is_approved:
        return Response({'error': 'user is disabled'}, status=status.HTTP_403_FORBIDDEN)
    
    # 检查密码是否正确
    if not check_password(password, user.password):
        return Response({'error': 'incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)

    # 生成 JWT token
    token = generate_token_for_user(user)

    return Response({
        'status': 'success',
        'message': 'login success',
        'user': {
            'user_id': user.user_id,
            'account': user.account,
            'role': user.role
        },
        'access': str(token.access_token),
        'refresh': str(token)
    })


# ---------- 注册账号权限 ----------


# 更新access token
@api_view(['POST'])
@permission_classes([IsApproved])
def access(request):
    refresh_token_str = request.data.get('refresh')

    if not refresh_token_str:
        return Response({'error': 'missing refresh token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 从字符串创建 RefreshToken 对象
        refresh = RefreshToken(refresh_token_str)

        # 验证通过，刷新 access token
        new_access = refresh.access_token

        return Response({
            'access': str(new_access)
        }, status=status.HTTP_200_OK)

    except TokenError as e:
        return Response({'error': 'invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


# 获取用户信息
@api_view(['GET'])
@permission_classes([IsApproved])
def get_user_info(request, user_id):
    # 获取指定 user_id 的用户
    user = get_object_or_404(User, pk=user_id)

    # 返回用户信息
    return Response({
        'user_id': user.user_id,
        'account': user.account,
        'is_approved': user.is_approved,
        'role': user.role,
        'create_time': user.create_time,
    }, status=status.HTTP_200_OK)

# 渔民注册
@api_view(['POST'])
@permission_classes([IsApproved])
def register_fisher(request):
    user = request.user

    # 检查用户是否已经注册为渔民
    if hasattr(user, 'fisher'):
        return Response({'error': 'user already registered as fisher'}, status=status.HTTP_400_BAD_REQUEST)

    # 创建渔民
    fisher = Fisher.objects.create(user=user)

    return Response({
        'status': 'success',
        'message': 'register success',
        'fisher': {
            'fisher_id': fisher.fisher_id,
            'user_id': user.user_id,
            'account': user.account
        }
    }, status=status.HTTP_201_CREATED)


# ---------- 管理员权限 ----------


# 获取用户列表
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_list(request):
    users = User.objects.all()
    user_list = []

    # 遍历添加用户信息到列表
    for user in users:
        user_list.append
        ({
            'user_id': user.user_id,
            'account': user.account,
            'is_approved': user.is_approved,
            'create_time': user.create_time,
            'role': user.role
        })

    return Response({
        'status': 'success',
        'user_list': user_list
    })


# 更新用户信息
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user_info(request, user_id):
    data = request.data
    account = data.get('account')
    password = data.get('password')
    role = data.get('role')

    # 检查参数是否缺失
    if not account and not password and not role:
        return Response({'error': 'missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查用户是否已经注册
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

    # 更新用户信息
    if account:
        user.account = account
    if password:
        user.password = make_password(password)
    if role:
        user.role = role

    user.save()

    return Response({
        'status': 'success',
        'message': 'update success',
        'user': {
            'user_id': user.user_id,
            'account': user.account,
            'role': user.role
        }
    })


# 获取渔民列表
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_fisher_list(request):
    fishers = Fisher.objects.all()
    fisher_list = []

    # 遍历添加渔民信息到列表
    for fisher in fishers:
        fisher_list.append({
            'fisher_id': fisher.fisher_id,
            'user_id': fisher.user.user_id,
            'account': fisher.user.account,
            'is_approved': fisher.user.is_approved,
            'create_time': fisher.user.create_time
        })

    return Response({
        'status': 'success',
        'fisher_list': fisher_list
    })