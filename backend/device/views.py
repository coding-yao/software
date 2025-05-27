from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def device_status(request):
    """
    设备状态
    """
    data = {
        "status": 200,
        "message": "success",
        "data": {
            "device_id": "DEVICE_001",
            "main_control": {
                "version": "v1.0.0",
                "temperature": 35.5
            },
            "secondary_control": {
                "connection_status": "断开"
            },
            "last_calibration": "2025-05-20 10:00:00"
        }
    }
    return JsonResponse(data)
