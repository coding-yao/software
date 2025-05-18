from django.urls import path
from . import views

urlpatterns = [
    # 主要信息 

    ## 水文气象数据
    path('hydro_meteorological/', views.hydro_meteorological, name='hydro_meteorological'),
    path('historical_data/', views.historical_data, name='historical_data'),
    path('get_provinces/', views.get_provinces, name='get_provinces'),
    path('get_basins/', views.get_basins, name='get_basins'),
    path('get_stations/', views.get_stations, name='get_stations'),
    path('device_status/', views.device_status, name='device_status'),
]