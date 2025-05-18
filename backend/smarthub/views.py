from django.shortcuts import render

# Create your views here.
# weather/views.py
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@api_view(['GET'])
@csrf_exempt
def get_weather(request):
    # 从请求中获取经纬度参数，如果没有则使用默认值(例如北京)
    latitude = request.GET.get('latitude', '39.9042')
    longitude = request.GET.get('longitude', '116.4074')
    
    # Open-Meteo API URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        return JsonResponse(weather_data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)