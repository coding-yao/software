import csv
import os
from django.http import JsonResponse
from django.conf import settings

def get_fish_data(request):
    # 定义CSV文件路径（假设文件存放在项目根目录的data文件夹中）
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'Fish.csv')
    
    try:
        # 初始化统计字典
        species_count = {}
        
        # 读取并处理CSV文件
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # 遍历每一行数据
            for row in csv_reader:
                species = row['Species']
                
                # 统计物种数量
                if species in species_count:
                    species_count[species] += 1
                else:
                    species_count[species] = 1
        
        # 转换为前端需要的格式
        result = [{"Species": k, "count": v} for k, v in species_count.items()]
        
        return JsonResponse(result, safe=False)
    
    except FileNotFoundError:
        return JsonResponse(
            {"error": "数据文件未找到"}, 
            status=404
        )
        
    except KeyError as e:
        return JsonResponse(
            {"error": f"CSV文件缺少必要列: {str(e)}"},
            status=400
        )
        
    except Exception as e:
        return JsonResponse(
            {"error": f"服务器内部错误: {str(e)}"},
            status=500
        )

# Create your views here.
