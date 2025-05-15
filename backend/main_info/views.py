from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def hydro_meteorological(request):
    """
    水文气象数据
    """
    data = {
        "status": 200,
        "message": "success",
        "data": {
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 5.0,
            "precipitation": 0.0
        }
    }
    return JsonResponse(data)