from django.urls import path
from . import views

urlpatterns = [
    # 认证接口 

    ## 用户登录
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('access/', views.access, name='access'),
    path('list/', views.get_user_list, name='get_user_list'),
    path('info/<int:user_id>/', views.get_user_info, name='get_user_info'),
    path('update/<int:user_id>/', views.update_user_info, name='update_user_info'),
    path('register_fisher/', views.register_fisher, name='register_fisher'),
    path('fisher_list/', views.get_fisher_list, name='get_fisher_list'),
]