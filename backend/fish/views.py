from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Fish
from core.permissions import IsAdminUser, IsFisher
from user.models import User, Fisher

# 获取自己鱼群的总信息
@api_view(['GET'])
@permission_classes([IsFisher])
def get_my_fish_status(request):
    user = get_object_or_404(User, id=request.user.id)
    fisher = user.fisher
    fish_list = Fish.objects.filter(fisher_id=fisher)
    data = []
    for fish in fish_list:
        data.append({
            'fish_id': fish.fish_id,
            'species': fish.species,
            'weight': fish.weight,
            'length1': fish.length1,
            'length2': fish.length2,
            'length3': fish.length3,
            'height': fish.height,
            'width': fish.width,
        })
    return Response({'fish_group': data}).status_code(status.HTTP_200_OK)


# 获取所有鱼群的总信息
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_fish_status(request):
    fish_list = Fish.objects.all()
    data = []
    for fish in fish_list:
        data.append({
            'fish_id': fish.fish_id,
            'fisher_id': fish.fisher_id.user.user_id,
            'species': fish.species,
            'weight': fish.weight,
            'length1': fish.length1,
            'length2': fish.length2,
            'length3': fish.length3,
            'height': fish.height,
            'width': fish.width,
        })
    return Response({'fish_group': data}).status_code(status.HTTP_200_OK)