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

class FishGrowthPredictor:
    def __init__(self):
        # 阶段1模型：预测length1
        self.model_stage1 = None
        
        # 阶段2模型：预测length2（使用length1）
        self.model_stage2 = None
        
        # 阶段3模型：预测length3（使用length1和length2）
        self.model_stage3 = None
        
        # 完整模型：直接预测length3（用于没有中间数据的情况）
        self.model_full = None
        
        # 其他模型
        self.model_weight_only = None
        self.model_weight_height = None
        
        # 预处理工具
        self.species_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.last_trained = None
        self.is_initialized = False
        self.growth_rates = {}  # 按物种存储平均生长速率
        self.feature_names = ['species_encoded', 'weight', 'height', 'width']
        self.feature_means = {}
        self.feature_stds = {}
        
    def initialize(self):
        """初始化模型，避免在应用启动时加载"""
        if not self.is_initialized:
            try:
                self.load_models()
                # print("✅ 模型加载成功")
                self.is_initialized = True
            except FileNotFoundError:
                # print("⚠️ 未找到已训练模型")
                self.is_initialized = False
        
    def train_models(self, fish_data):
        df = pd.DataFrame(list(fish_data.values(
            'species', 'weight', 'height', 'width', 
            'length1', 'length2', 'length3'
        )))
        
        # 数据清洗 - 确保所有必需字段都有值
        df = df.dropna(subset=['length1', 'length2', 'length3'])
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        if df.empty:
            return {
                "error": "无有效数据用于训练",
                "sample_count": 0,
                "species_count": 0
            }
        
        # 记录样本信息
        sample_count = len(df)
        species_count = df['species'].nunique()
        
        # 编码物种
        df['species_encoded'] = self.species_encoder.fit_transform(df['species'])
        
        # 计算生长速率并存储
        self._calculate_growth_rates(df)
        
        # 划分数据集
        X = df[['species_encoded', 'weight', 'height', 'width']]
        y1 = df['length1']
        y2 = df['length2']
        y3 = df['length3']
        
        # 使用相同的随机状态确保分割一致
        X_train, X_test, y1_train, y1_test = train_test_split(
            X, y1, test_size=0.2, random_state=42
        )
        
        # 获取对应的y2和y3
        _, _, y2_train, y2_test = train_test_split(
            X, y2, test_size=0.2, random_state=42
        )
        _, _, y3_train, y3_test = train_test_split(
            X, y3, test_size=0.2, random_state=42
        )
        
        # 标准化数值特征
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # 保存特征的均值和标准差（用于手动标准化）
        for i, name in enumerate(self.feature_names):
            self.feature_means[name] = self.scaler.mean_[i]
            self.feature_stds[name] = self.scaler.scale_[i]
        
        # 训练阶段1模型（预测length1）
        self.model_stage1 = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_stage1.fit(X_train_scaled, y1_train)
        
        # 准备阶段2数据（添加length1）
        X2_train = np.column_stack((X_train_scaled, y1_train))
        X2_test = np.column_stack((X_test_scaled, y1_test))
        
        # 训练阶段2模型（预测length2）
        self.model_stage2 = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_stage2.fit(X2_train, y2_train)
        
        # 准备阶段3数据（添加length1和length2）
        X3_train = np.column_stack((X2_train, y2_train))
        X3_test = np.column_stack((X2_test, y2_test))
        
        # 训练阶段3模型（预测length3）
        self.model_stage3 = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_stage3.fit(X3_train, y3_train)
        
        # 训练完整模型（直接预测length3）
        self.model_full = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_full.fit(X_train_scaled, y3_train)
        
        # 训练仅体重模型
        self.model_weight_only = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_weight_only.fit(X_train_scaled[:, :2], y3_train)
        
        # 训练体重+高度模型
        self.model_weight_height = RandomForestRegressor(n_estimators=75, random_state=42)
        self.model_weight_height.fit(X_train_scaled[:, :3], y3_train)
        
        # 评估模型
        mae_full = mean_absolute_error(y3_test, self.model_full.predict(X_test_scaled))
        
        # 使用三阶段模型进行预测
        stage3_pred = self._predict_stage3(X_test_scaled, y1_test, y2_test)
        mae_stage3 = mean_absolute_error(y3_test, stage3_pred)
        
        self.last_trained = timezone.now()
        self.is_initialized = True
        
        return {
            "mae_full": mae_full,
            "mae_stage3": mae_stage3,
            "message": "多阶段模型训练成功",
            "sample_count": sample_count,
            "species_count": species_count
        }
    
    def _standardize_features(self, features):
        """
        手动标准化特征，处理不同数量的输入特征
        """
        # 记录输入特征
        print(f"原始特征: {features}")

        # 创建包含所有特征的数组（用训练集的均值填充缺失特征）
        full_features = np.array([
            features.get('species_encoded', self.feature_means['species_encoded']),
            features.get('weight', self.feature_means['weight']),
            features.get('height', self.feature_means['height']),
            features.get('width', self.feature_means['width'])
        ])
        print(f"完整特征向量: {full_features}")
        
        standardized = []
        for i, name in enumerate(self.feature_names):
            mean = self.feature_means[name]
            std = self.scaler.scale_[i]  # 使用scaler的scale_属性
            value = full_features[i]
            standardized_value = (value - mean) / std
            standardized.append(standardized_value)
            
            print(f"特征 {name}: 原始值={value:.2f}, 均值={mean:.2f}, 标准差={std:.2f}, 标准化后={standardized_value:.2f}")
            
        standardized_array = np.array([standardized])
        print(f"标准化后特征: {standardized_array}")
        
        return standardized_array
    
    def _calculate_growth_rates(self, df):
        """计算并存储各物种的平均生长速率"""
        self.growth_rates = {}
        for species in df['species'].unique():
            species_df = df[df['species'] == species]
            
            # 计算阶段1生长速率（length1到length2）
            rate1 = ((species_df['length2'] - species_df['length1']) / species_df['length1']).mean()
            
            # 计算阶段2生长速率（length2到length3）
            rate2 = ((species_df['length3'] - species_df['length2']) / species_df['length2']).mean()
            
            self.growth_rates[species] = {
                'rate1': rate1,
                'rate2': rate2
            }
    
    def _predict_stage3(self, features, length1, length2):
        """使用三阶段模型预测length3"""
        # 确保length1和length2是数组形式
        if not isinstance(length1, np.ndarray):
            length1 = np.array(length1).reshape(-1, 1)
        if not isinstance(length2, np.ndarray):
            length2 = np.array(length2).reshape(-1, 1)
        
        # 预测length1（如果未提供）
        if length1 is None:
            length1 = self.model_stage1.predict(features)
            length1 = length1.reshape(-1, 1)
        
        # 准备阶段2数据
        stage2_features = np.hstack((features, length1))
        
        # 预测length2（如果未提供）
        if length2 is None:
            length2 = self.model_stage2.predict(stage2_features)
            length2 = length2.reshape(-1, 1)
        
        # 准备阶段3数据
        stage3_features = np.hstack((stage2_features, length2))
        
        # 预测length3
        return self.model_stage3.predict(stage3_features)
    
    def predict_length3(self, species, weight, height=None, width=None, length1=None, length2=None):
        # 编码物种
        try:
            species_encoded = self.species_encoder.transform([species])[0]
        except ValueError:
            species_encoded = -1  # 未知物种
        
        # 准备特征字典
        features = {
            'species_encoded': species_encoded,
            'weight': weight,
        }
        
        # 添加可选特征
        if height is not None:
            features['height'] = height
        if width is not None:
            features['width'] = width
        
        # 标准化特征
        features_scaled = self._standardize_features(features)
        
        # 根据可用数据选择最佳模型
        if length1 is not None and length2 is not None:
            # 使用完整的三阶段模型
            prediction = self._predict_stage3(features_scaled, [length1], [length2])[0]
            model_type = "full_growth"
        elif length1 is not None:
            # 使用阶段2和3模型
            prediction = self._predict_stage3(features_scaled, [length1], None)[0]
            model_type = "two_stage"
        elif 'height' in features and 'width' in features:
            # 使用完整模型
            prediction = self.model_full.predict(features_scaled)[0]
            model_type = "full"
        elif 'height' in features:
            # 使用体重+高度模型
            # 只使用前3个特征
            prediction = self.model_weight_height.predict(features_scaled[:, :3])[0]
            model_type = "weight_height"
        else:
            # 使用仅体重模型
            # 只使用前2个特征
            prediction = self.model_weight_only.predict(features_scaled[:, :2])[0]
            model_type = "weight_only"
        
        # 添加基于生长速率的预测（作为参考）
        growth_prediction = None
        if species in self.growth_rates:
            if length2 is not None:
                # 如果有length2，使用阶段2生长速率
                growth_rate = self.growth_rates[species]['rate2']
                growth_prediction = length2 * (1 + growth_rate)
            elif length1 is not None:
                # 如果有length1，使用阶段1和2生长速率
                growth_rate1 = self.growth_rates[species]['rate1']
                growth_rate2 = self.growth_rates[species]['rate2']
                estimated_length2 = length1 * (1 + growth_rate1)
                growth_prediction = estimated_length2 * (1 + growth_rate2)
        
        return {
            "predicted_length3": prediction,
            "model_type": model_type,
            "growth_rate_prediction": growth_prediction
        }
    
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

predictor = FishGrowthPredictor()