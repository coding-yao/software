import csv
import os
import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from collections import defaultdict

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
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 5.0,
            "precipitation": 0.0
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
        # 使用province_name_mapping的键作为省份列表（简称）
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
        
        # 将省份简称转换为全称
        province_full = province_name_mapping.get(province)
        if not province_full:
            return JsonResponse({
                "status": 400,
                "message": "无效的省份名称",
                "data": None
            })
        
        data_dir = os.path.join(settings.BASE_DIR, 'data', 'water_quality_by_time')
        basins = set()
        
        # 遍历所有月份文件夹
        for month_dir in os.listdir(data_dir):
            month_path = os.path.join(data_dir, month_dir)
            if os.path.isdir(month_path):
                # 遍历该月所有数据文件
                for file_name in os.listdir(month_path):
                    if file_name.endswith('.json'):
                        file_path = os.path.join(month_path, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                daily_data = json.load(f)
                                # 检查数据格式
                                if 'tbody' in daily_data:
                                    for record in daily_data['tbody']:
                                        if len(record) >= 2 and record[0] == province_full and record[1]:
                                            basins.add(record[1])
                        except Exception as e:
                            print(f"Error reading file {file_path}: {str(e)}")
                            continue
        
        basins_list = sorted(list(basins))
        print(f"{province_full}的流域列表: {basins_list}")  # 添加调试信息
        
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": basins_list
        })
    except Exception as e:
        print(f"Error in get_basins: {str(e)}")  # 添加调试信息
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
        
        # 将省份简称转换为全称
        province_full = province_name_mapping.get(province)
        if not province_full:
            return JsonResponse({
                "status": 400,
                "message": "无效的省份名称",
                "data": None
            })
        
        data_dir = os.path.join(settings.BASE_DIR, 'data', 'water_quality_by_time')
        stations = set()
        
        # 遍历所有月份文件夹
        for month_dir in os.listdir(data_dir):
            month_path = os.path.join(data_dir, month_dir)
            if os.path.isdir(month_path):
                # 遍历该月所有数据文件
                for file_name in os.listdir(month_path):
                    if file_name.endswith('.json'):
                        file_path = os.path.join(month_path, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                daily_data = json.load(f)
                                if 'tbody' in daily_data:
                                    for record in daily_data['tbody']:
                                        if (len(record) >= 3 and 
                                            record[0] == province_full and 
                                            record[1] == basin and 
                                            record[2]):
                                            if '>' in record[2] and '<' in record[2]:
                                                stations.add(record[2].split('>')[1].split('<')[0])
                                            else:
                                                stations.add(record[2])
                        except Exception as e:
                            print(f"读取文件 {file_path} 时出错: {str(e)}")
                            continue
        
        stations_list = sorted(list(stations))
        print(f"{province_full} {basin}的断面列表: {stations_list}")  # 添加调试信息
        
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": stations_list
        })
    except Exception as e:
        print(f"获取断面列表时出错: {str(e)}")  # 添加调试信息
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
        province = request.GET.get('province')
        if not province:
            province = '北京'
        basin = request.GET.get('basin')
        if not basin:
            basin = '海河流域'
        station = request.GET.get('station')
        if not station:
            station = '古北口'
        
        print(f"地域范围 - 省份: {province}, 流域: {basin}, 断面: {station}")  # 调试信息
        
        # 将省份简称转换为全称
        province_full = province_name_mapping.get(province)
        if not province_full:
            return JsonResponse({
                "status": 400,
                "message": "无效的省份名称",
                "data": None
            })
        
        # 处理日期参数
        end_date = request.GET.get('end_date')
        if not end_date:
            end_date = '2020-12-17'
        
        start_date = request.GET.get('start_date')
        if not start_date:
            start_date = '2020-05-10'
        
        print(f"日期范围 - {start_date} 至 {end_date}")  # 调试信息
        
        # 构建数据文件路径
        data_dir = os.path.join(settings.BASE_DIR, 'data', 'water_quality_by_time')
        
        # 存储结果数据
        result_data = {
            'dates': [],
            'water_temperature': [],
            'ph': [],
            'dissolved_oxygen': []
        }
        
        # 遍历日期范围内的数据文件
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_datetime:
            date_str = current_date.strftime('%Y-%m-%d')
            file_path = os.path.join(data_dir, current_date.strftime('%Y-%m'), f'{date_str}.json')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    # print(f"正在读取文件: {file_path}")  # 添加调试信息
                    daily_data = json.load(f)
                    
                    # 查找对应省份、流域、断面的数据
                    if 'tbody' in daily_data:
                        for record in daily_data['tbody']:
                            if (len(record) >= 8 and 
                                record[0] == province_full and 
                                record[1] == basin and 
                                (record[2] == station or 
                                 ('>' in record[2] and '<' in record[2] and 
                                  record[2].split('>')[1].split('<')[0] == station))):
                                
                                result_data['dates'].append(date_str)
                                # 提取水温、pH值和溶解氧数据
                                try:
                                    # 处理水温
                                    if record[5] == '--':
                                        water_temp = None
                                    else:
                                        water_temp = record[5].split('>')[1].split('<')[0]
                                        water_temp = None if water_temp == '--' else water_temp
                                    
                                    # 处理pH值
                                    if record[6] == '--':
                                        ph = None
                                    else:
                                        ph = record[6].split('>')[1].split('<')[0]
                                        ph = None if ph == '--' else ph
                                    
                                    # 处理溶解氧
                                    if record[7] == '--':
                                        do = None
                                    else:
                                        do = record[7].split('>')[1].split('<')[0]
                                        do = None if do == '--' else do
                                    
                                    # 转换数值并添加到结果中
                                    result_data['water_temperature'].append(float(water_temp) if water_temp else None)
                                    result_data['ph'].append(float(ph) if ph else None)
                                    result_data['dissolved_oxygen'].append(float(do) if do else None)
                                    # print(f"水温: {water_temp}, pH: {ph}, 溶解氧: {do}")
                                except Exception as e:
                                    print(f"处理数据值时出错: {str(e)}, 记录: {record}")
                                    continue
                                break
            
            current_date += timedelta(days=1)
        
        print(f"查询完成，找到 {len(result_data['dates'])} 条数据")  # 调试信息
        
        return JsonResponse({
            "status": 200,
            "message": "success",
            "data": result_data
        })
        
    except Exception as e:
        print(f"获取历史数据时出错: {str(e)}")  # 调试信息
        return JsonResponse({
            "status": 500,
            "message": str(e),
            "data": None
        })
    