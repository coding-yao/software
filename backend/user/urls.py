from django.urls import path
from . import views

urlpatterns = [
    # 认证接口 

    ## 用户登录
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
]