<template>
  <NavBar current-page="smarthub" />
  <div class="main-content">
    <WeatherWidget />
    
    <!-- 添加AI对话区域 -->
    <div class="ai-chat-section">
      <h2>AI 智能助手</h2>
      <AIChat />
    </div>

    <div class="video-container">
      <iframe 
        :src="`//player.bilibili.com/player.html?bvid=${bvid}&page=1`"
        scrolling="no"
        frameborder="no"
        allowfullscreen="true"
      ></iframe>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import WeatherWidget from '@/components/WeatherWidget.vue';
import AIChat from '@/components/AIChat.vue'; // 导入AI对话组件

export default {
    components: {
        NavBar,
        WeatherWidget,
        AIChat // 注册AI对话组件
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
    display: grid;
    grid-template-columns: 1fr 1fr; /* 两列布局 */
    grid-gap: 20px; /* 列间距 */
}

/* 视频容器样式保持不变 */
.video-container {
    grid-column: span 2; /* 视频占据两列 */
    margin-top: 20px;
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 宽高比 */
    overflow: hidden;
    border-radius: 8px;
}

.video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
}

/* 新增AI对话区域样式 */
.ai-chat-section {
    background-color: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    height: 400px; /* 固定高度 */
    display: flex;
    flex-direction: column;
}

.ai-chat-section h2 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #2c3e50;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 10px;
}

/* 响应式布局 - 移动设备适配 */
@media (max-width: 768px) {
    .main-content {
        grid-template-columns: 1fr; /* 单列布局 */
    }
    
    .video-container {
        grid-column: span 1; /* 视频只占一列 */
    }
    
    .ai-chat-section {
        height: 400px; /* 移动端高度调整 */
    }
}
</style>