from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
from .models import Fish
from core.permissions import IsAdminUser, IsFisher
from user.models import User, Fisher


# 鱼群总体信息接口
## 获取自己鱼群的总信息

@api_view(['GET'])
@permission_classes([IsFisher])
def get_my_fish_status(request):
    user = request.user
    fisher = get_object_or_404(Fisher, user=user)

    # 可选的时间筛选参数
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')

    fish_qs = Fish.objects.filter(fisher_id=fisher)

    if start_time_str:
        start_time = parse_datetime(start_time_str)
        if start_time:
            fish_qs = fish_qs.filter(created_at__gte=start_time)

    if end_time_str:
        end_time = parse_datetime(end_time_str)
        if end_time:
            fish_qs = fish_qs.filter(created_at__lte=end_time)

    total_fish = fish_qs.count()
    total_weight = fish_qs.aggregate(weight_sum=models.Sum('weight'))['weight_sum'] or 0
    species_count = fish_qs.values('species').distinct().count()

    # 假设模型中有字段 is_alive 和 created_at 来判断新增/死亡情况
    new_fish = fish_qs.filter(created_at__gte=start_time).count() if start_time_str else 0
    dead_fish = fish_qs.filter(is_alive=False).count() if 'is_alive' in [f.name for f in Fish._meta.fields] else 0

    return Response({
        'total_fish': total_fish,
        'total_weight': total_weight,
        'species_count': species_count,
        'new_fish': new_fish,
        'dead_fish': dead_fish,
    })


## 获取所有鱼群的总信息
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


# 鱼群数据详细接口
## 获取鱼列表
@api_view(['GET'])
@permission_classes([IsFisher])
def get_fish_list(request):
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