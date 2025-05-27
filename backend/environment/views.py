from django.shortcuts import render
import os
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from collections import defaultdict
from . import models  

# 省份名称映射字典（简称到全称的映射）
province_name_mapping = {
    '北京': '北京市',
    '天津': '天津市',
    '河北': '河北省',
    '山西': '山西省',
    '内蒙古': '内蒙古自治区',
    '辽宁': '辽宁省',
    '吉林': '吉林省',
    '黑龙江': '黑龙江省',
    '上海': '上海市',
    '江苏': '江苏省',
    '浙江': '浙江省',
    '安徽': '安徽省',
    '福建': '福建省',
    '江西': '江西省',
    '山东': '山东省',
    '河南': '河南省',
    '湖北': '湖北省',
    '湖南': '湖南省',
    '广东': '广东省',
    '广西': '广西壮族自治区',
    '海南': '海南省',
    '重庆': '重庆市',
    '四川': '四川省',
    '贵州': '贵州省',
    '云南': '云南省',
    '西藏': '西藏自治区',
    '陕西': '陕西省',
    '甘肃': '甘肃省',
    '青海': '青海省',
    '宁夏': '宁夏回族自治区',
    '新疆': '新疆维吾尔自治区',
    '台湾': '台湾省',
    '香港': '香港特别行政区',
    '澳门': '澳门特别行政区'
}

@api_view(['GET'])
def hydro_meteorological(request):
    """
    水文气象数据
    """
    data = {
        "status": 200,
        "message": "success",
        "data": {
            "voltage": 25.9,
            "salinity": 34.16,
            "dissolved_oxygen": 0.0,
            "turbidity": 2.05,
            "ph": 8.37,
            "temperature": 15.0,
        }
    }
    return JsonResponse(data)

@api_view(['GET'])
def get_provinces(request):
    """
    获取所有省份列表
    返回的是省份的简称（如：北京、天津等）
    """
    try:
        provinces = list(province_name_mapping.keys())
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": sorted(provinces)
        })
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": str(e),
            "data": None
        })

@api_view(['GET'])
def get_basins(request):
    """
    根据省份获取流域列表
    """
    try:
        province = request.GET.get('province')
        if not province:
            return JsonResponse({
                "status": 400,
                "message": "请提供省份参数",
                "data": None
            })
        
        province_full = province_name_mapping.get(province)
        if not province_full:
            return JsonResponse({
                "status": 400,
                "message": "无效的省份名称",
                "data": None
            })
        
        # 从数据库查询该省份的所有流域
        basins = models.WaterData.objects.filter(location=province_full).values_list('province', flat=True).distinct()
        basins_list = sorted(list(basins))
        
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": basins_list
        })
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": str(e),
            "data": None
        })

@api_view(['GET'])
def get_stations(request):
    """
    根据省份和流域获取断面列表
    """
    try:
        province = request.GET.get('province')
        basin = request.GET.get('basin')
        
        if not province or not basin:
            return JsonResponse({
                "status": 400,
                "message": "请提供省份和流域参数",
                "data": None
            })
        
        province_full = province_name_mapping.get(province)
        if not province_full:
            return JsonResponse({
                "status": 400,
                "message": "无效的省份名称",
                "data": None
            })
        
        # 从数据库查询该省份和流域的所有断面
        stations = models.WaterData.objects.filter(
            location=province_full,
            province=basin
        ).values_list('domain', flat=True).distinct()
        
        stations_list = sorted(list(stations))
        
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": stations_list
        })
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": str(e),
            "data": None
        })

@api_view(['GET'])
def historical_data(request):
    """
    历史记录
    参数：
    - province: 省份
    - basin: 流域
    - station: 断面名称
    - start_date: 开始日期
    - end_date: 结束日期
    """
    try:
        # 获取请求参数
        province = request.GET.get('province', '北京')
        basin = request.GET.get('basin', '海河流域')
        station = request.GET.get('station', '古北口')
        end_date = request.GET.get('end_date', '2020-05-17')
        start_date = request.GET.get('start_date', '2020-05-10')
        
        # 将省份简称转换为全称
        province_full = province_name_mapping.get(province)
        if not province_full:
            return JsonResponse({
                "status": 400,
                "message": "无效的省份名称",
                "data": None
            })
        
        # 查询数据库
        queryset = models.WaterData.objects.filter(
            location=province_full,
            province=basin,
            domain=station,
            time__gte=start_date,
            time__lte=end_date
        ).order_by('time')
        
        # 构建结果数据
        result_data = {
            'dates': [],
            'water_temperature': [],
            'ph': [],
            'dissolved_oxygen': []
        }
        
        for record in queryset:
            result_data['dates'].append(record.time)
            result_data['water_temperature'].append(record.temperature)
            result_data['ph'].append(record.ph)
            result_data['dissolved_oxygen'].append(record.oxygen)
        
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": result_data
        })
        
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": str(e),
            "data": None
        })