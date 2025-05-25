from django.urls import path
from . import views


urlpatterns = [
    path('my_fish_status/', views.get_my_fish_status, name='get_my_fish_status'),
    path('all_fish_status/', views.get_all_fish_status, name='get_all_fish_status'),
    path('fish_list/', views.get_fish_list, name='get_fish_list'),
    path('all_fish_list/', views.get_all_fish_list, name='get_all_fish_list'),
]