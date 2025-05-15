from django.urls import path
from . import views

urlpatterns = [
    # 主要信息 

    ## 水文气象数据
    path('hydro-meteorological/', views.hydro_meteorological, name='hydro_meteorological'),
]