from django.urls import path
from . import views


urlpatterns = [
    path('my_fish_status/', views.get_my_fish_status, name='get_my_fish_status'),
    path('all_fish_status/', views.get_all_fish_status, name='get_all_fish_status'),
]