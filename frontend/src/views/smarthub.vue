<template>
  <NavBar current-page="smarthub" />
  <div class="main-content">
    <div class="dashboard-grid">
      <!-- 左侧列：天气和图片识别 -->
      <div class="left-column">
        <WeatherWidget />
        <div class="image-recognition-section">
          <h2>图片内容识别</h2>
          <ImageRecognition />
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
import ImageRecognition from '@/components/ImageRecognition.vue'; // 导入图片识别组件

export default {
    components: {
        NavBar,
        WeatherWidget,
        AIChat,
        ImageRecognition // 注册图片识别组件
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
    margin-top: 80px; /* 为固定定位的导航栏留出空间 */
    padding: 20px;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr; /* 两列布局 */
    grid-gap: 24px; /* 增加间距 */
    grid-template-areas:
        "left-column ai-chat"
        "video video";
}

.left-column {
    grid-area: left-column;
    display: flex;
    flex-direction: column;
    gap: 24px; /* 子组件之间的间距 */
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

.ai-chat-section h2 {
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
    .image-recognition-section {
        padding: 16px;
    }
}

/* 卡片悬停效果 */
.image-recognition-section:hover,
.ai-chat-section:hover {
    transform: translateY(-5px);
    transition: transform 0.3s ease;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
}
</style>