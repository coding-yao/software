from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from zhipuai import ZhipuAI
import base64
import requests

@csrf_exempt
def deepseek_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            messages = data.get('messages', [])
            
            client = OpenAI(
                api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Replace with your actual API key
                base_url="https://api.deepseek.com"
            )
            
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
        client = ZhipuAI(api_key="xxxxxxxxxxxxxxxxxxx")  # 替换 GLM API密钥
        
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