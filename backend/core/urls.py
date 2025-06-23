from django.urls import path
from . import views

urlpatterns = [
    path('check_alert/', views.check_alert, name='check_alert')
]