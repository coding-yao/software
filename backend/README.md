#

## 基础依赖

1. Django REST Framework
    - 安装：`pip install djangorestframework`
    - 导入：`from rest_framework import xxx`

2. JWT 身份认证
    - 安装：`pip install djangorestframework-simplejwt`
    - 导入: `from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView`

## 运行

`backend` 文件夹下运行 `python manage.py runserver`
