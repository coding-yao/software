from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


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
