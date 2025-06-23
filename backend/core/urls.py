from django.urls import path
from . import views

urlpatterns = [
    path('upload_fish_csv/', views.upload_fish_csv, name='upload_fish_csv'),
    path('download_fish_csv/', views.download_fish_csv, name='download_fish_csv'),
    path('download_all_fish_csv/', views.download_all_fish_csv, name='download_all_fish_csv')
]