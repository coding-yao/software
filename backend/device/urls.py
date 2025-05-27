from django.urls import path
from . import views

urlpatterns = [
    # 设备状态
    path('device_status/', views.device_status, name='device_status'),
]