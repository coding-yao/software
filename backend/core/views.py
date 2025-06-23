import csv
import datetime
from django.http import HttpResponse
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .permissions import IsAdminUser, IsFisher
from fish.models import Fish
from user.models import Fisher

# 上传数据
@api_view(['POST'])
@permission_classes([IsFisher])
def upload_fish_csv(request):    
    # 获取并验证 fisher_id
    try:
        fisher_id = int(request.data.get("fisher_id"))
    except (ValueError, TypeError):
        return Response({'error': 'fisher_id 必须是有效的整数'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not fisher_id:
        return Response({'error': '缺少 fisher_id 参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取并验证csv数据文件
    if 'file' not in request.FILES:
        return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        return Response({'error': '请上传 CSV 文件'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        # 验证表头
        required_fields = {'species', 'weight', 'length1'}
        if not required_fields.issubset(reader.fieldnames):
            missing = required_fields - set(reader.fieldnames)
            return Response({'error': f'缺少必要字段: {", ".join(missing)}'}, status=400)
        
        fish_instances = []
        errors = []
        
        with transaction.atomic():
            for i, row in enumerate(reader, start=2):  # 从第2行开始
                try:                    
                    # 创建鱼对象
                    fish = Fish(
                        fisher_id=fisher_id,
                        species=row['species'],
                        weight=float(row['weight']),
                        length1=float(row['length1']),
                        length2=float(row.get('length2', 0)),
                        length3=float(row.get('length3', 0)),
                        height=float(row.get('height', 0)),
                        width=float(row.get('width', 0)),
                        is_alive=row.get('is_alive', 'True').lower() == 'true',
                    )
                    
                    # 可选字段处理
                    if row.get('died_at'):
                        fish.died_at = datetime.datetime.fromisoformat(row['died_at'])
                    
                    fish_instances.append(fish)
                except Fisher.DoesNotExist:
                    errors.append(f'第 {i} 行：渔民账号 {row["fisher_account"]} 不存在')
                except Exception as e:
                    errors.append(f'第 {i} 行：{str(e)}')
        
        if errors:
            return Response({'errors': errors}, status=400)
        
        Fish.objects.bulk_create(fish_instances)
        return Response({'message': f'成功导入 {len(fish_instances)} 条记录'}, status=201)
    
    except UnicodeDecodeError:
        return Response({'error': '文件编码错误，确保使用 UTF-8'}, status=400)
    

# 下载鱼类数据
@api_view(['GET'])
@permission_classes([IsFisher])
def download_fish_csv(request):
    # 获取 fisher_id
    fisher_id = request.user.fisher.id
    
    # 创建响应对象，设置为 CSV 格式
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fish_data.csv"'
    
    # 创建 CSV 写入器
    writer = csv.writer(response)
    
    # 写入表头
    writer.writerow([
        'id', 'fisher_account', 'species', 'weight', 'length1', 
        'length2', 'length3', 'height', 'width', 'is_alive', 'died_at'
    ])
    
    # 查询并写入数据
    fish_data = Fish.objects.select_related('fisher').filter(fisher_id=fisher_id)
    
    for fish in fish_data:
        writer.writerow([
            fish.id,
            fish.fisher.id,
            fish.species,
            fish.weight,
            fish.length1,
            fish.length2,
            fish.length3,
            fish.height,
            fish.width,
            fish.is_alive,
            fish.died_at.isoformat() if fish.died_at else '',
        ])
    
    return response


# 下载所有鱼类数据
@api_view(['GET'])
@permission_classes([IsAdminUser])
def download_all_fish_csv(request):        
    # 创建响应对象，设置为 CSV 格式
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fish_data.csv"'
    
    # 创建 CSV 写入器
    writer = csv.writer(response)
    
    # 写入表头
    writer.writerow([
        'id', 'fisher_account', 'species', 'weight', 'length1', 
        'length2', 'length3', 'height', 'width', 'is_alive', 'died_at'
    ])
    
    # 查询并写入数据
    fish_data = Fish.objects.select_related('fisher').all()
    
    for fish in fish_data:
        writer.writerow([
            fish.id,
            fish.fisher.id,
            fish.species,
            fish.weight,
            fish.length1,
            fish.length2,
            fish.length3,
            fish.height,
            fish.width,
            fish.is_alive,
            fish.died_at.isoformat() if fish.died_at else '',
        ])
    
    return response