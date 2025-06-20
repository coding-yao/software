from django.urls import path
from . import views

urlpatterns = [
    path('deepseek/', views.deepseek_chat, name='deepseek_chat'),
    path('recognize-image/', views.recognize_image, name='recognize_image'),
]