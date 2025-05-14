# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get_fish_data/', views.get_fish_data, name='get_fish_data'),  #  这行的作用： 匹配前端的请求路径 /reg  
    # 也就是接收axios.post(http://localhost:5000/api/get_fish_data, data)所发来的信息 匹配的就是/reg
    # 然后用views的get_fish_data函数进行处理。
]