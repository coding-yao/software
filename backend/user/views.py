from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from core.permissions import IsAdminUser, IsActive, IsFisher
from .models import User, Fisher


def generate_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['account'] = user.account
    refresh['role'] = user.role
    return refresh



# 用户注册
@api_view(['POST'])
def register_user(request):
    data = request.data
    account = data.get('account')
    password = data.get('password')
    role = data.get('role', 'viewer')

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
        is_active=False,
        role=role
    )

    if role == 'fisher':
        Fisher.objects.create(user=user)

    return Response({
        'status': 'success',
        'message': 'register success',
        'user': {
            'user_id': user.id,
            'account': user.account,
            'role': user.role
        },
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
    if not user.is_active:
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
            'user_id': user.id,
            'account': user.account,
            'role': user.role
        },
        'access': str(token.access_token),
        'refresh': str(token)
    })


# ---------- 注册账号权限 ----------


# 更新access token
@api_view(['POST'])
@permission_classes([IsActive])
def access(request):
    print("in access,请求新的token")
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
@permission_classes([IsActive])
def get_user_info(request, id):
    # 获取指定 user_id 的用户
    user = get_object_or_404(User, pk=id)

    # 返回用户信息
    return Response({
        'user_id': user.id,
        'account': user.account,
        'is_active': user.is_active,
        'role': user.role,
        'create_time': user.create_time,
    }, status=status.HTTP_200_OK)

# 渔民注册
@api_view(['POST'])
@permission_classes([IsActive])
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
            'fisher_id': fisher.id,
            'user_id': user.id,
            'account': user.account
        }
    }, status=status.HTTP_201_CREATED)


# ---------- 渔民权限 ----------


@api_view(['POST'])
@permission_classes([IsFisher])
def update_thresholds(request):
    """
    更新渔民的预警阈值配置
    """
    try:
        # 获取当前用户的 fisher 对象
        fisher = request.user.fisher

        # 获取请求数据
        data = request.data
        
        # 更新阈值字段（仅更新请求中包含的字段）
        if 'weight_deviation_multiplier' in data:
            fisher.weight_deviation_multiplier = data['weight_deviation_multiplier']
        
        if 'length_min' in data:
            fisher.length_min = data['length_min']
        
        if 'length_max' in data:
            fisher.length_max = data['length_max']
        
        if 'aspect_ratio_min' in data:
            fisher.aspect_ratio_min = data['aspect_ratio_min']
        
        if 'aspect_ratio_max' in data:
            fisher.aspect_ratio_max = data['aspect_ratio_max']
        
        if 'height_width_ratio_min' in data:
            fisher.height_width_ratio_min = data['height_width_ratio_min']
        
        if 'height_width_ratio_max' in data:
            fisher.height_width_ratio_max = data['height_width_ratio_max']
        
        if 'daily_mortality_rate_threshold' in data:
            fisher.daily_mortality_rate_threshold = data['daily_mortality_rate_threshold']
        
        # 保存更新
        fisher.save()
        
        # 返回成功响应
        return Response({
            'message': '阈值更新成功',
            'thresholds': {
                'weight_deviation_multiplier': fisher.weight_deviation_multiplier,
                'length_min': fisher.length_min,
                'length_max': fisher.length_max,
                # 'aspect_ratio_min': fisher.aspect_ratio_min,
                # 'aspect_ratio_max': fisher.aspect_ratio_max,
                # 'height_width_ratio_min': fisher.height_width_ratio_min,
                # 'height_width_ratio_max': fisher.height_width_ratio_max,
                'daily_mortality_rate_threshold': fisher.daily_mortality_rate_threshold,
            }
        }, status=status.HTTP_200_OK)
        
    except Fisher.DoesNotExist:
        return Response({"error": "未找到该渔民的信息"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"更新阈值失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# ---------- 管理员权限 ----------


# 获取用户列表
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_list(request):
    print(request.user)
    users = User.objects.all()
    user_list = []

    # 遍历添加用户信息到列表
    for user in users:
        user_list.append({
            'user_id': user.id,
            'account': user.account,
            'is_active': user.is_active,
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
        user = User.objects.get(id=user_id)
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
            'user_id': user.id,
            'account': user.account,
            'role': user.role
        }
    })


# 更新用户信息
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def approve_user(request, user_id):
    # 检查用户是否已经注册
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

    # 更新用户信息
    user.is_active = True

    user.save()

    return Response({
        'status': 'success',
        'message': 'activate success',
        'user': {
            'user_id': user.id,
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
            'fisher_id': fisher.id,
            'user_id': fisher.user.id,
            'account': fisher.user.account,
            'is_active': fisher.user.is_active,
            'create_time': fisher.user.create_time
        })

    return Response({
        'status': 'success',
        'fisher_list': fisher_list
    })