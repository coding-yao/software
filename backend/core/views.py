import csv
from datetime import date, timedelta
from django.db.models import Avg, StdDev
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .permissions import IsFisher
from fish.models import Fish
from user.models import Fisher


# 预警模块
@api_view(['GET'])
@permission_classes([IsFisher])
def check_alert(request):
    try:
        # 获取当前用户的fisher对象
        fisher = request.user.fisher
        
        alerts = []
        
        # 获取目标渔民的鱼群
        fish_qs = Fish.objects.filter(fisher=fisher)
        
        # 按鱼种缓存统计数据
        species_stats_cache = {}
        
        # 检查单条鱼异常
        for fish in fish_qs:
            thresholds = {
                'weight_deviation_multiplier': fisher.weight_deviation_multiplier,
                'length_min': fisher.length_min,
                'length_max': fisher.length_max,
                'aspect_ratio_min': fisher.aspect_ratio_min,
                'aspect_ratio_max': fisher.aspect_ratio_max,
                'height_width_ratio_min': fisher.height_width_ratio_min,
                'height_width_ratio_max': fisher.height_width_ratio_max,
            }
            
            # 获取或计算该鱼种的统计数据
            cache_key = f"{fisher.id}_{fish.species}"
            if cache_key not in species_stats_cache:
                # 过滤相同渔民和鱼种的鱼
                species_fish = Fish.objects.filter(
                    fisher=fisher,
                    species=fish.species
                )
                
                if not species_fish.exists():
                    continue  # 如果没有同种类的鱼，跳过检查
                
                stats = species_fish.aggregate(avg_weight=Avg('weight'), std_weight=StdDev('weight'))
                
                # 避免标准差为零
                stats['std_weight'] = stats['std_weight'] or 0.1
                species_stats_cache[cache_key] = stats
            
            species_stats = species_stats_cache.get(cache_key)
            if not species_stats:
                continue  # 统计数据不存在，跳过检查
            
            # 检查重量异常
            weight_deviation = abs(fish.weight - species_stats['avg_weight']) / species_stats['std_weight']
            if weight_deviation > thresholds['weight_deviation_multiplier']:
                severity = 'high' if weight_deviation > 5.0 else 'medium'
                alerts.append({
                    'fish_id': fish.id,
                    'fish_species':fish.species,
                    'alert_type': '重量异常',
                    'severity': severity,
                    'message': (
                        f"{fish.species}鱼ID#{fish.id}重量异常：{fish.weight}kg，"
                        f"比同鱼种平均重量{species_stats['avg_weight']:.2f}kg偏差{weight_deviation:.2f}个标准差"
                    )
                })
            
            # 检查长度异常
            if fish.length1 < thresholds['length_min']:
                alerts.append({
                    'fish_id': fish.id,
                    'fish_species':fish.species,
                    'alert_type': '长度异常',
                    'severity': 'medium',
                    'message': f"{fish.species}鱼ID#{fish.id}长度异常：{fish.length1}cm，低于最小阈值{thresholds['length_min']}cm"
                })
            
            if fish.length1 > thresholds['length_max']:
                alerts.append({
                    'fish_id': fish.id,
                    'fish_species':fish.species,
                    'alert_type': '长度异常',
                    'severity': 'high',
                    'message': f"{fish.species}鱼ID#{fish.id}长度异常：{fish.length1}cm，超过最大阈值{thresholds['length_max']}cm"
                })
            
            # 检查体型比例异常
            # if fish.width > 0:
            #     aspect_ratio = fish.length1 / fish.width
            #     height_width_ratio = fish.height / fish.width
                
            #     if aspect_ratio < thresholds['aspect_ratio_min']:
            #         alerts.append({
            #             'fish_id': fish.id,
            #             'alert_type': 'size_ratio',
            #             'severity': 'medium',
            #             'message': f"鱼ID#{fish.id}体型异常：长宽比{aspect_ratio:.2f}，低于最小阈值{thresholds['aspect_ratio_min']}"
            #         })
                
            #     if aspect_ratio > thresholds['aspect_ratio_max']:
            #         alerts.append({
            #             'fish_id': fish.id,
            #             'alert_type': 'size_ratio',
            #             'severity': 'medium',
            #             'message': f"鱼ID#{fish.id}体型异常：长宽比{aspect_ratio:.2f}，超过最大阈值{thresholds['aspect_ratio_max']}"
            #         })
                
            #     if height_width_ratio < thresholds['height_width_ratio_min']:
            #         alerts.append({
            #             'fish_id': fish.id,
            #             'alert_type': 'size_ratio',
            #             'severity': 'medium',
            #             'message': f"鱼ID#{fish.id}体型异常：高宽比{height_width_ratio:.2f}，低于最小阈值{thresholds['height_width_ratio_min']}"
            #         })
                
            #     if height_width_ratio > thresholds['height_width_ratio_max']:
            #         alerts.append({
            #             'fish_id': fish.id,
            #             'alert_type': 'size_ratio',
            #             'severity': 'medium',
            #             'message': f"鱼ID#{fish.id}体型异常：高宽比{height_width_ratio:.2f}，超过最大阈值{thresholds['height_width_ratio_max']}"
            #         })
        
        # 检查死亡率异常
        # today = date.today()
        # yesterday = today - timedelta(days=1)
        
        # 统计昨天的死亡鱼数量
        dead_fish_count = Fish.objects.filter(
            fisher=fisher,
            is_alive=False,
            # died_at__date=yesterday
        ).count()
        
        # 统计存活鱼数量
        alive_fish_count = fish_qs.filter(is_alive=True).count()
        
        # 计算活跃鱼群的死亡率（仅计算昨天存活的鱼）
        if alive_fish_count > 0:
            mortality_rate = dead_fish_count / alive_fish_count
            
            if mortality_rate > fisher.daily_mortality_rate_threshold:
                severity = 'high' if mortality_rate > 0.05 else 'medium'
                alerts.append({
                    'fish_id': None,  # 群体预警
                    'alert_type': '鱼群死亡率',
                    'severity': severity,
                    'message': (
                        f"鱼群死亡率：{mortality_rate:.2%}，"
                        f"超过阈值{100*fisher.daily_mortality_rate_threshold:.2f}%，"
                        f"死亡数量：{dead_fish_count}，存活数量：{alive_fish_count}"
                    )
                })
        
        return Response(alerts)
    
    except Fisher.DoesNotExist:
        return Response({"error": "未找到该渔民的信息"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"发生错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)