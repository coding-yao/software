import os
import joblib
import pandas as pd
import numpy as np
from django.db import models
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from django.utils import timezone
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class FishPredictor:
    def __init__(self):
        self.model_full = None
        self.model_weight_only = None
        self.model_weight_height = None
        self.species_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.last_trained = None
        self.is_initialized = False
        
    def initialize(self):
        """初始化模型，避免在应用启动时加载"""
        if not self.is_initialized:
            try:
                self.load_models()
                print("✅ 模型加载成功")
                self.is_initialized = True
            except FileNotFoundError:
                print("⚠️ 未找到已训练模型")
                self.is_initialized = False
    
    def train_models(self, fish_data):
        # 数据预处理
        df = pd.DataFrame(list(fish_data.values(
            'species', 'weight', 'height', 'width', 'length3'
        )))
        
        # 处理可能的空值
        df = df.dropna(subset=['length3'])
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        if df.empty:
            print("⚠️ 无有效数据用于训练")
            return 0, 0
        
        # 编码鱼种
        df['species_encoded'] = self.species_encoder.fit_transform(df['species'])
        
        # 划分数据集
        X = df[['species_encoded', 'weight', 'height', 'width']]
        y = df['length3']
        
        if len(df) < 10:  # 数据量太少时使用全部数据
            X_train, X_test, y_train, y_test = X, X, y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 标准化数值特征
        if len(X_train) > 0:
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test) if len(X_test) > 0 else X_train_scaled
        else:
            print("⚠️ 无训练数据")
            return 0, 0
        
        # 训练完整特征模型
        self.model_full = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_full.fit(X_train_scaled, y_train)
        
        # 训练仅体重模型
        self.model_weight_only = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_weight_only.fit(X_train_scaled[:, :2], y_train)  # 只使用物种和体重
        
        # 训练体重+高度模型
        self.model_weight_height = RandomForestRegressor(n_estimators=75, random_state=42)
        self.model_weight_height.fit(X_train_scaled[:, :3], y_train)  # 物种、体重、高度
        
        # 评估模型
        if len(X_test) > 0:
            mae_full = mean_absolute_error(y_test, self.model_full.predict(X_test_scaled))
            mae_weight = mean_absolute_error(y_test, self.model_weight_only.predict(X_test_scaled[:, :2]))
        else:
            mae_full, mae_weight = 0, 0
        
        self.last_trained = timezone.now()
        self.is_initialized = True
        return mae_full, mae_weight
    
    def predict_length(self, species, weight, height=None, width=None):
        if not self.is_initialized:
            return None, "uninitialized"
        
        # 编码物种
        try:
            species_encoded = self.species_encoder.transform([species])[0]
        except ValueError:
            # 未知物种处理
            species_encoded = -1  # 特殊值表示未知
        
        # 根据可用特征选择模型
        if height is not None and width is not None and self.model_full:
            features = [[species_encoded, weight, height, width]]
            model = self.model_full
            model_type = "full"
        elif height is not None and self.model_weight_height:
            features = [[species_encoded, weight, height]]
            model = self.model_weight_height
            model_type = "weight_height"
        elif self.model_weight_only:
            features = [[species_encoded, weight]]
            model = self.model_weight_only
            model_type = "weight_only"
        else:
            return None, "no_model"
        
        # 标准化特征
        if model == self.model_full:
            try:
                features_scaled = self.scaler.transform(features)
            except:
                features_scaled = features
        else:
            features_scaled = features
        
        # 预测
        try:
            prediction = model.predict(features_scaled)[0]
            return prediction, model_type
        except:
            return None, "prediction_error"
    
    def save_models(self, path='fish_models.joblib'):
        joblib.dump({
            'model_full': self.model_full,
            'model_weight_only': self.model_weight_only,
            'model_weight_height': self.model_weight_height,
            'species_encoder': self.species_encoder,
            'scaler': self.scaler,
            'last_trained': self.last_trained
        }, path)
    
    def load_models(self, path='fish_models.joblib'):
        path = os.path.join(settings.BASE_DIR, 'fish_models.joblib')
        try:
            logger.info(f"尝试加载模型: {path}")
            models = joblib.load(path)
            self.model_full = models['model_full']
            self.model_weight_only = models['model_weight_only']
            self.model_weight_height = models['model_weight_height']
            self.species_encoder = models['species_encoder']
            self.scaler = models['scaler']
            self.last_trained = models['last_trained']
            self.is_initialized = True
            logger.info("✅ 模型加载成功")
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {str(e)}")
            self.is_initialized = False
            raise

# 创建全局预测器实例
predictor = FishPredictor()