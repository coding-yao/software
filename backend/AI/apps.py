from django.apps import AppConfig
from .predictor import predictor

class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AI'
    def ready(self):
        # 仅标记预测器，不立即初始化
        # 实际初始化将在第一次请求时进行
        print("✅ 鱼类预测器已准备")
        predictor.initialize()
