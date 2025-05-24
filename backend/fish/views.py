from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Count, Sum
from .models import Fish
from core.permissions import IsAdminUser, IsFisher
from user.models import Fisher


# 获取当前用户（渔夫）鱼群的总体状态信息
@api_view(['GET'])
@permission_classes([IsFisher])
def get_my_fish_status(request):
    fisher = get_object_or_404(Fisher, user=request.user)

    # 可选时间参数
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')
    start_time = parse_datetime(start_time_str) if start_time_str else None
    end_time = parse_datetime(end_time_str) if end_time_str else None

    fish_qs = Fish.objects.filter(fisher_id=fisher)
    if start_time:
        fish_qs = fish_qs.filter(created_at__gte=start_time)
    if end_time:
        fish_qs = fish_qs.filter(created_at__lte=end_time)

    total_fish = fish_qs.count()
    total_weight = fish_qs.aggregate(weight_sum=models.Sum('weight'))['weight_sum'] or 0
    species_count = fish_qs.values('species').distinct().count()
    new_fish = fish_qs.filter(created_at__gte=start_time).count() if start_time else 0
    has_is_alive = any(f.name == 'is_alive' for f in Fish._meta.fields)
    dead_fish = fish_qs.filter(is_alive=False).count() if has_is_alive else 0

    return Response({
        'total_fish': total_fish,
        'total_weight': total_weight,
        'species_count': species_count,
        'new_fish': new_fish,
        'dead_fish': dead_fish,
    }, status=status.HTTP_200_OK)


# 获取所有鱼群的总体信息（仅管理员）
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_fish_status(request):
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')

    fish_qs = Fish.objects.all()

    # 时间筛选
    if start_time_str:
        start_time = parse_datetime(start_time_str)
        if start_time:
            fish_qs = fish_qs.filter(added_at__gte=start_time)
    else:
        start_time = None

    if end_time_str:
        end_time = parse_datetime(end_time_str)
        if end_time:
            fish_qs = fish_qs.filter(added_at__lte=end_time)

    total_fish = fish_qs.count()
    total_weight = fish_qs.aggregate(weight_sum=Sum('weight'))['weight_sum'] or 0

    # 每种品种的数量与总重
    species_stats = fish_qs.values('species').annotate(
        count=Count('id'),
        weight=Sum('weight')
    )

    # 新增数量（按起始时间）
    new_fish = fish_qs.filter(added_at__gte=start_time).count() if start_time else 0

    # 死亡数量（is_alive=False）
    dead_fish = fish_qs.filter(is_alive=False).count()

    return Response({
        'total_fish': total_fish,
        'total_weight': total_weight,
        'species_details': list(species_stats),
        'new_fish': new_fish,
        'dead_fish': dead_fish,
    }, status=status.HTTP_200_OK)


# 获取当前渔民的所有鱼数据详细列表
@api_view(['GET'])
@permission_classes([IsFisher])
def get_fish_list(request):
    fisher = get_object_or_404(Fisher, user=request.user)
    fish_list = Fish.objects.filter(fisher_id=fisher)
    data = [{
        'fish_id': fish.id,
        'species': fish.species,
        'weight': fish.weight,
        'length1': fish.length1,
        'length2': fish.length2,
        'length3': fish.length3,
        'height': fish.height,
        'width': fish.width,
    } for fish in fish_list]
    return Response({'fish_group': data}, status=status.HTTP_200_OK)
