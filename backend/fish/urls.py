from django.urls import path
from . import views


urlpatterns = [
    path('status/', views.get_status, name='get_status'),
]