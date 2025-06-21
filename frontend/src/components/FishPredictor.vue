<template>
  <div class="fish-predictor">
    <!-- 模型状态显示 -->
    <div v-if="modelStatus === 'loading'" class="status-message loading">
      <div class="spinner"></div>
      <p>模型加载中，请稍候...</p>
    </div>
    
    <div v-if="modelStatus === 'ready'">
      <div class="model-info-card">
        <div class="status-indicator ready"></div>
        <div class="model-details">
          <h3>鱼类体长预测模型</h3>
          <p v-if="modelInfo.last_trained">
            最后训练时间: {{ formatDate(modelInfo.last_trained) }}
          </p>
          <p>支持生长阶段预测</p>
        </div>
      </div>
      
      <div class="prediction-section">
        <h3 class="section-title">预测参数</h3>
        <div class="fish-predictor-form">
          <div class="form-group">
            <label>鱼种</label>
            <select v-model="form.species" required>
              <option v-for="species in speciesList" :key="species" :value="species">
                {{ species }}
              </option>
            </select>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>体重 (克)</label>
              <input type="number" v-model.number="form.weight" min="1" required>
            </div>
            
            <div class="form-group">
              <label>高度 (厘米)</label>
              <input type="number" v-model.number="form.height" min="0.1" step="0.1" placeholder="可选">
            </div>
            
            <div class="form-group">
              <label>宽度 (厘米)</label>
              <input type="number" v-model.number="form.width" min="0.1" step="0.1" placeholder="可选">
            </div>
          </div>
          
          <!-- 添加生长阶段数据输入 -->
          <div class="growth-stage-section">
            <h4>生长阶段数据（可选）</h4>
            <div class="form-row">
              <div class="form-group">
                <label>阶段1体长 (cm)</label>
                <input type="number" v-model.number="form.length1" min="0.1" step="0.1">
                <span class="hint">length1</span>
              </div>
              
              <div class="form-group">
                <label>阶段2体长 (cm)</label>
                <input type="number" v-model.number="form.length2" min="0.1" step="0.1">
                <span class="hint">length2</span>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <button type="button" @click="predict" :disabled="loading">
              <span v-if="!loading">预测最终体长</span>
              <span v-else>计算中...</span>
            </button>
          </div>
        </div>
        
        <div v-if="error" class="error-message">
          <h3>预测错误</h3>
          <p>{{ error }}</p>
        </div>
        
        <div v-if="result" class="result-section">
          <h3 class="section-title">预测结果</h3>
          <div class="prediction-result">
            <div class="prediction-value">
              {{ result.predicted_length3 }} <span>cm</span>
            </div>
            <div class="prediction-meta">
              <div class="model-type">
                {{ getModelName(result.model_used) }}
              </div>
              <div class="confidence">
                最终体长预测
              </div>
            </div>
          </div>
          
          <!-- 生长速率预测 -->
          <div v-if="result.growth_rate_prediction" class="growth-prediction">
            <div class="growth-prediction-value">
              基于生长速率预测: {{ result.growth_rate_prediction }} cm
            </div>
            <div class="growth-explanation">
              （根据该鱼种历史生长速率估算）
            </div>
          </div>
          
          <div class="comparison-section">
            <h4>历史数据对比</h4>
            <div v-if="result.historical_comparison.sample_count > 0">
              <p class="comparison-description">
                体重在 {{ Math.round(form.weight * 0.8) }}g - {{ Math.round(form.weight * 1.2) }}g 的 {{ form.species }}
              </p>
              
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ result.historical_comparison.min_length }}</div>
                  <div class="stat-label">最小体长 (cm)</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ result.historical_comparison.avg_length }}</div>
                  <div class="stat-label">平均体长 (cm)</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ result.historical_comparison.max_length }}</div>
                  <div class="stat-label">最大体长 (cm)</div>
                </div>
              </div>
              
              <div class="similar-fish">
                <h5>相似鱼类样本</h5>
                <div class="fish-samples">
                  <div v-for="fish in result.historical_comparison.similar_fish" :key="fish.id" class="fish-sample">
                    <div class="fish-id">ID: {{ fish.id }}</div>
                    <div class="fish-weight">体重: {{ fish.weight }}g</div>
                    <div class="fish-length">体长: {{ fish.length3 }}cm</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-data">
              <p>未找到相似的历史数据</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        species: 'Bream',
        weight: 300,
        height: null,
        width: null
      },
      speciesList: ['Bream', 'Roach', 'Whitefish', 'Perch', 'Pike', 'Smelt'],
      loading: false,
      error: null,
      result: null,
      modelStatus: 'loading',
      modelError: '',
      modelInfo: {},
      debugInfo: {
        path: '',
        error: ''
      }
    };
  },
  created() {
    // 初始加载时尝试加载本地模型
    this.loadLocalModel();
    this.fetchSpecies();
  },
  methods: {
    async loadLocalModel() {
      this.modelStatus = 'loading';
      this.modelError = '';
      
      try {
        // 调用后端API加载本地模型
        const response = await axios.post('http://localhost:8000/api/AI/load-local-model/');
        
        if (response.data.success) {
          this.modelStatus = 'ready';
          this.modelInfo = {
            ...response.data,
            source: '本地预训练模型'
          };
        } else {
          throw new Error(response.data.message || '加载本地模型失败');
        }
      } catch (error) {
        this.modelStatus = 'error';
        if (error.response) {
          this.modelError = error.response.data.error || '加载本地模型失败';
          this.debugInfo = {
            path: error.response.config.url,
            error: error.response.data.detail || JSON.stringify(error.response.data)
          };
        } else {
          this.modelError = error.message || '加载本地模型失败';
          this.debugInfo.error = error.message;
        }
      }
    },
    
    async initializeModel() {
      this.modelStatus = 'loading';
      try {
        // 调用后端API重新训练模型
        const response = await axios.post('http://localhost:8000/api/AI/train-models/');
        
        if (response.data.message) {
          this.modelStatus = 'ready';
          this.modelInfo = {
            last_trained: new Date().toISOString(),
            ...response.data,
            source: '重新训练模型'
          };
        } else {
          throw new Error('模型训练失败');
        }
      } catch (error) {
        this.modelStatus = 'error';
        if (error.response) {
          this.modelError = error.response.data.error || '模型训练失败';
        } else {
          this.modelError = error.message || '模型训练失败';
        }
      }
    },
    
    async fetchSpecies() {
      try {
        const response = await axios.get('http://localhost:8000/api/AI/species/');
        this.speciesList = response.data.species;
        if (this.speciesList.length > 0) {
          this.form.species = this.speciesList[0];
        }
      } catch (error) {
        console.error('获取鱼种列表失败:', error);
      }
    },
    
    async predict() {
      this.loading = true;
      this.error = null;
      this.result = null;
      
      try {
        const payload = { 
          species: this.form.species,
          weight: this.form.weight,
          height: this.form.height,
          width: this.form.width,
          length1: this.form.length1,
          length2: this.form.length2
        };
        // 移除空值
        Object.keys(payload).forEach(key => {
          if (payload[key] === null || payload[key] === '') {
            delete payload[key];
          }
        });
        
        const response = await axios.post('http://localhost:8000/api/AI/predict-length/', payload);
        this.result = response.data;
      } catch (error) {
        let errorMsg = '预测失败，请稍后重试';
        
         if (error.response) {
          if (error.response.data?.error) {
            errorMsg = error.response.data.error;
          } else if (error.response.status === 400) {
            errorMsg = '请求参数不正确';
          } else if (error.response.status === 500) {
            errorMsg = '服务器内部错误';
          }
        } else if (error.message) {
          errorMsg = error.message;
        }
        
        this.error = errorMsg;
        console.error('预测错误:', error);
      } finally {
        this.loading = false;
      }
    },
    
    getModelName(modelType) {
      const modelNames = {
        "full_growth": "三阶段生长模型",
        "two_stage": "两阶段生长模型",
        "full": "完整特征模型",
        "weight_height": "体重+高度模型",
        "weight_only": "仅体重模型"
      };
      return modelNames[modelType] || modelType;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
  }
};
</script>

<style scoped>
.fish-predictor {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 25px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid #e1e8ed;
}

.section-title {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin-top: 0;
  margin-bottom: 25px;
  font-weight: 600;
}

.status-message {
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 25px;
}

.status-message.loading {
  background: #e3f2fd;
  color: #1976d2;
}

.status-message.error {
  background: #ffebee;
  color: #c62828;
}

.status-message.warning {
  background: #fff8e1;
  color: #f57c00;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(41, 128, 185, 0.2);
  border-top: 5px solid #2980b9;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.action-button {
  background: #2980b9;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  margin: 5px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: inline-block;
}

.action-button:hover {
  background: #1c6ea4;
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.model-info-card {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #3498db;
}

.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 15px;
}

.status-indicator.ready {
  background: #2ecc71;
  box-shadow: 0 0 10px rgba(46, 204, 113, 0.5);
}

.model-details {
  flex: 1;
}

.model-details h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.model-details p {
  margin: 5px 0;
  color: #555;
  font-size: 0.95rem;
}

.prediction-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.fish-predictor-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

select, input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dce4ec;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 1rem;
  transition: all 0.3s ease;
}

select:focus, input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

button {
  background: linear-gradient(to right, #3498db, #2980b9);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.result-section {
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid #ecf0f1;
}

.prediction-result {
  display: flex;
  align-items: center;
  gap: 25px;
  margin-bottom: 30px;
}

.prediction-value {
  font-size: 3.5rem;
  font-weight: 700;
  color: #2980b9;
}

.prediction-value span {
  font-size: 1.5rem;
  color: #7f8c8d;
}

.prediction-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.model-type {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.confidence {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.comparison-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-top: 25px;
}

.comparison-description {
  color: #555;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.stat-item {
  background: white;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #ecf0f1;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2980b9;
  margin-bottom: 8px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.similar-fish h5 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 15px;
}

.fish-samples {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.fish-sample {
  background: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #ecf0f1;
  transition: all 0.3s ease;
}

.fish-sample:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
}

.fish-id, .fish-weight, .fish-length {
  margin: 5px 0;
}

.fish-id {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.fish-weight, .fish-length {
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #95a5a6;
  font-style: italic;
}

.debug-info {
  background: rgba(0, 0, 0, 0.05);
  padding: 10px;
  border-radius: 6px;
  margin: 15px 0;
  font-family: monospace;
  font-size: 0.9rem;
}

.debug-info p {
  margin: 5px 0;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
}

@media (max-width: 768px) {
  .fish-predictor {
    padding: 15px;
  }
  
  .prediction-result {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .prediction-value {
    font-size: 2.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>