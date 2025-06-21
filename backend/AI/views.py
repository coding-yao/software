from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from zhipuai import ZhipuAI
import base64
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .predictor import predictor
from fish.models import Fish
from django.utils import timezone
from datetime import timedelta
import os
from django.conf import settings
# from rest_framework.permissions import IsAdminUser
from .models import APIKey

def get_api_key(service):
    try:
        return APIKey.objects.get(service=service).key
    except APIKey.DoesNotExist:
        return None

@csrf_exempt
def deepseek_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            messages = data.get('messages', [])
            
            api_key = get_api_key('DEEPSEEK')
            if not api_key:
                return JsonResponse({'error': 'DeepSeek API key not configured'}, status=500)
            
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )
            
            return JsonResponse({
                'reply': response.choices[0].message.content
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def recognize_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    api_key = get_api_key('GLM')
    if not api_key:
        return JsonResponse({'error': 'GLM API key not configured'}, status=500)
    
    # 获取上传的图片
    image_file = request.FILES.get('image')
    if not image_file:
        return JsonResponse({'error': 'No image provided'}, status=400)
    
    try:
        # 将图片转为base64
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        image_url = f"data:image/{image_file.name.split('.')[-1]};base64,{base64_image}"
        
        # 调用GLM API
        client = ZhipuAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="GLM-4V-Flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "详细描述图片内容"},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        # 解析响应
        result = response.choices[0].message.content
        return JsonResponse({'result': result})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

class TrainModelsView(APIView):
    def post(self, request):
        # 获取所有鱼类数据
        fish_data = Fish.objects.filter(
            length1__isnull=False, 
            length2__isnull=False, 
            length3__isnull=False
        )
        
        # 验证数据完整性
        if len(fish_data) < 10:
            missing_data = Fish.objects.filter(
                Q(length1__isnull=True) | 
                Q(length2__isnull=True) | 
                Q(length3__isnull=True)
            ).count()
            
            return Response({
                "error": f"训练数据不足，需要至少10个完整样本（包含所有生长阶段数据）",
                "available_samples": len(fish_data),
                "missing_data_samples": missing_data,
                "required_samples": 10
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 调用训练方法，返回一个结果字典
            result = predictor.train_models(fish_data)
            
            # 保存模型
            predictor.save_models()
            
            return Response({
                "message": result.get("message", "模型训练成功"),
                "last_trained": timezone.now().isoformat(),
                "mae_full": result.get("mae_full", 0),
                "mae_stage3": result.get("mae_stage3", 0),
                "species_count": result.get("species_count", 0),
                "sample_count": result.get("sample_count", 0)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"训练过程中出错: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PredictLengthView(APIView):
    def post(self, request):
        data = request.data
        
        # 验证必要参数
        if 'species' not in data or 'weight' not in data:
            return Response(
                {"error": "Species and weight are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 确保数值参数转换为float
            species = data['species']
            weight = float(data['weight'])
            height = float(data['height']) if 'height' in data and data['height'] else None
            width = float(data['width']) if 'width' in data and data['width'] else None
            length1 = float(data['length1']) if 'length1' in data and data['length1'] else None
            length2 = float(data['length2']) if 'length2' in data and data['length2'] else None
            
            # 预测体长
            prediction = predictor.predict_length3(
                species, weight, height, width, length1, length2
            )
        except ValueError as ve:
            return Response(
                {"error": f"Invalid parameter value: {str(ve)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Prediction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 获取历史数据对比
        weight_range = (max(1, weight * 0.8), weight * 1.2)  # 确保最小值不小于1
        similar_fish = Fish.objects.filter(
            species=species,
            weight__range=weight_range,
            length3__isnull=False
        ).order_by('weight')[:100]  # 限制最多100条
        
        # 计算历史统计信息
        if similar_fish.exists():
            lengths = [fish.length3 for fish in similar_fish]
            hist_min = min(lengths)
            hist_max = max(lengths)
            hist_avg = sum(lengths) / len(lengths)
            hist_count = len(lengths)
        else:
            hist_min = hist_max = hist_avg = None
            hist_count = 0
        
        return Response({
            "predicted_length3": round(prediction['predicted_length3'], 2),
            "model_used": prediction['model_type'],
            "growth_rate_prediction": round(prediction['growth_rate_prediction'], 2) if prediction['growth_rate_prediction'] else None,
            "historical_comparison": {
                "min_length": hist_min,
                "max_length": hist_max,
                "avg_length": round(hist_avg, 2) if hist_avg else None,
                "sample_count": hist_count,
                "similar_fish": [
                    {"id": fish.id, "weight": fish.weight, "length3": fish.length3} 
                    for fish in similar_fish[:10]  # 限制返回数量
                ]
            }
        })

class SpeciesListView(APIView):
    def get(self, request):
        # 获取所有鱼种
        species = Fish.objects.values_list('species', flat=True).distinct()
        return Response({"species": list(species)})

class ModelStatusView(APIView):
    def get(self, request):
        # 检查模型是否初始化
        if not predictor.is_initialized:
            try:
                predictor.load_models()
            except:
                pass
        
        # 获取模型信息
        status = "ready" if predictor.is_initialized else "uninitialized"
        
        # 获取训练数据统计
        try:
            fish_data = Fish.objects.filter(
                length1__isnull=False, 
                length2__isnull=False, 
                length3__isnull=False
            )
            species_count = fish_data.values('species').distinct().count()
            sample_count = fish_data.count()
        except:
            species_count = 0
            sample_count = 0
        
        return Response({
            "status": status,
            "is_initialized": predictor.is_initialized,
            "last_trained": predictor.last_trained.isoformat() if predictor.last_trained else None,
            "species_count": species_count,
            "sample_count": sample_count,
            "model_type": "多阶段生长模型"
        })
    
class LoadLocalModelView(APIView):
    def post(self, request):
        try:
            # 指定本地模型路径
            model_path = os.path.join(settings.BASE_DIR, 'fish_models.joblib')
            
            # 确保文件存在
            if not os.path.exists(model_path):
                return Response({
                    "success": False,
                    "error": f"模型文件不存在: {model_path}",
                    "path": model_path
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 加载模型
            predictor.load_models(path=model_path)
            
            # 获取模型信息
            fish_data = Fish.objects.filter(length3__isnull=False)
            species_count = fish_data.values('species').distinct().count()
            sample_count = fish_data.count()
            
            return Response({
                "success": True,
                "message": "本地模型加载成功",
                "is_initialized": predictor.is_initialized,
                "last_trained": predictor.last_trained.isoformat() if predictor.last_trained else None,
                "species_count": species_count,
                "sample_count": sample_count,
                "model_path": model_path
            })
        except Exception as e:
            return Response({
                "success": False,
                "error": f"加载本地模型失败: {str(e)}",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class APIKeyView(APIView):
    # permission_classes = [IsAdminUser]
    
    def get(self, request):
        keys = APIKey.objects.all()
        result = {key.service: key.key for key in keys}
        return Response(result)
    
    def post(self, request):
        service = request.data.get('service')
        key_value = request.data.get('key')
        
        if not service or not key_value:
            return Response({'error': 'Missing service or key'}, status=400)
            
        api_key, created = APIKey.objects.update_or_create(
            service=service,
            defaults={'key': key_value}
        )
        
        return Response({
            'status': 'created' if created else 'updated',
            'service': api_key.service,
            'last_updated': api_key.last_updated
        })