<template>
  <NavBar current-page="smarthub" />
  <div class="main-content">
    <div class="dashboard-grid">
      <!-- 左侧列：天气、图片识别和新增的鱼类预测 -->
      <div class="left-column">
        <WeatherWidget />
        <div class="image-recognition-section">
          <h2>图片内容识别</h2>
          <ImageRecognition />
        </div>
        
        <!-- 新增鱼类体长预测模块 -->
        <div class="fish-predictor-section">
          <h2>鱼类体长预测</h2>
          <FishPredictor />
        </div>
      </div>
      
      <!-- 右侧列：AI对话 -->
      <div class="ai-chat-section">
        <h2>AI 智能养殖助手</h2>
        <AIChat />
      </div>
      
      <!-- 视频区域 -->
      <div class="video-container">
        <iframe 
          :src="`//player.bilibili.com/player.html?bvid=${bvid}&page=1`"
          scrolling="no"
          frameborder="no"
          allowfullscreen="true"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import WeatherWidget from '@/components/WeatherWidget.vue';
import AIChat from '@/components/AIChat.vue';
import ImageRecognition from '@/components/ImageRecognition.vue';
import FishPredictor from '@/components/FishPredictor.vue';

export default {
    components: {
        NavBar,
        WeatherWidget,
        AIChat,
        ImageRecognition,
        FishPredictor
    },
    data() {
        return {
            bvid: "BV1X64y1j7Ff"
        };
    }
}
</script>

<style scoped>
.main-content {
    margin-top: 80px; 
    padding: 20px;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr; 
    grid-gap: 24px; 
    grid-template-areas:
        "left-column ai-chat"
        "video video";
}

.left-column {
    grid-area: left-column;
    display: flex;
    flex-direction: column;
    gap: 24px; 
}

.ai-chat-section {
    grid-area: ai-chat;
    background-color: #ffffff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid #eaeaea;
}

/* 新增鱼类预测区域样式 */
.fish-predictor-section {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    border: 1px solid #eaeaea;
    display: flex;
    flex-direction: column;
}

.fish-predictor-section h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #2c3e50;
    font-size: 1.5rem;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f4f8;
}

/* 图片识别区域样式 */
.image-recognition-section {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    border: 1px solid #eaeaea;
    display: flex;
    flex-direction: column;
}

.image-recognition-section h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #2c3e50;
    font-size: 1.5rem;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f4f8;
}

/* 视频容器样式 */
.video-container {
    grid-area: video;
    margin-top: 24px;
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 宽高比 */
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    background-color: #000;
}

.video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
}

/* 响应式布局 - 移动设备适配 */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr; /* 单列布局 */
        grid-template-areas:
            "left-column"
            "ai-chat"
            "video";
        grid-gap: 16px;
    }
    
    .video-container {
        margin-top: 16px;
    }
    
    .left-column,
    .ai-chat-section,
    .image-recognition-section,
    .fish-predictor-section {
        padding: 16px;
    }
}

/* 卡片悬停效果 */
.image-recognition-section:hover,
.ai-chat-section:hover,
.fish-predictor-section:hover {
    transform: translateY(-5px);
    transition: transform 0.3s ease;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
}

/* 鱼类预测组件内部样式 */
.fish-predictor-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 12px;
}

.form-group.full-width {
  grid-column: span 2;
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 500;
}

input, select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #f8fafc;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

input:focus, select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

button {
  background-color: #3182ce;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
  font-size: 0.95rem;
}

button:hover {
  background-color: #2b6cb0;
}

button:disabled {
  background-color: #cbd5e0;
  cursor: not-allowed;
}

.hint {
  font-size: 0.8rem;
  color: #718096;
  margin-top: 4px;
}

.result-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.prediction {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.prediction-value {
  color: #3182ce;
  margin-left: 8px;
  font-size: 1.4rem;
}

.model-type {
  font-size: 0.85rem;
  color: #718096;
  margin-left: 12px;
}

.comparison-card {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
  border: 1px solid #e2e8f0;
}

.comparison-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #2d3748;
  display: flex;
  align-items: center;
}

.comparison-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  background: white;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.stat-label {
  font-size: 0.8rem;
  color: #718096;
  margin-bottom: 4px;
}

.stat-value {
  font-weight: 600;
  font-size: 1.1rem;
  color: #3182ce;
}

.similar-fish-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
  font-size: 0.9rem;
}

.similar-fish-table th,
.similar-fish-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.similar-fish-table th {
  background-color: #edf2f7;
  font-weight: 600;
  color: #4a5568;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #a0aec0;
  font-style: italic;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  color: #3182ce;
}

.error-message {
  background-color: #fff5f5;
  color: #e53e3e;
  padding: 12px;
  border-radius: 6px;
  margin: 10px 0;
  border: 1px solid #fed7d7;
}
</style>