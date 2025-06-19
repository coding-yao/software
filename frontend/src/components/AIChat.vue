<template>
  <div class="ai-chat-container">
    <!-- 对话历史区域 -->
    <div class="chat-history" ref="historyContainer">
      <div v-for="(msg, index) in messages" :key="index" 
           :class="['message', msg.role]">
        <div class="message-header">
          <span v-if="msg.role === 'user'">👤 你</span>
          <span v-else>🤖 AI助手</span>
        </div>
        <div class="message-content">
          {{ msg.content }}
        </div>
      </div>
      <div v-if="isLoading" class="message assistant">
        <div class="message-header">🤖 AI助手</div>
        <div class="message-content loading">
          <div class="dot-flashing"></div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input">
      <textarea 
        v-model="userInput" 
        placeholder="输入您的问题..."
        @keyup.enter.exact="sendMessage"
        :disabled="isLoading"
      ></textarea>
      <button 
        @click="sendMessage" 
        :disabled="isLoading || !userInput.trim()"
        class="send-button"
      >
        <span v-if="!isLoading">发送</span>
        <span v-else>思考中...</span>
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AIChat',
  data() {
    return {
      messages: [
        { role: 'assistant', content: '你好！我是AI鱼类养殖助手，有什么可以帮您的吗？' }
      ],
      userInput: '',
      isLoading: false,
      apiUrl: 'http://localhost:8000/api/AI/deepseek/' // 替换为你的Django后端地址
    };
  },
  methods: {
    async sendMessage() {
      if (!this.userInput.trim() || this.isLoading) return;
      
      // 添加用户消息
      const userMessage = this.userInput;
      this.messages.push({ role: 'user', content: userMessage });
      this.userInput = '';
      
      this.isLoading = true;
      
      try {
        // 调用后端API
        const response = await axios.post(this.apiUrl, {
          messages: this.messages
        });
        
        // 添加AI回复
        this.messages.push({
          role: 'assistant',
          content: response.data.reply
        });
        
        // 滚动到底部
        this.$nextTick(() => {
          const container = this.$refs.historyContainer;
          container.scrollTop = container.scrollHeight;
        });
        
      } catch (error) {
        console.error('API调用失败:', error);
        this.messages.push({
          role: 'assistant',
          content: '抱歉，处理您的请求时出错了，请稍后再试。'
        });
      } finally {
        this.isLoading = false;
      }
    }
  },
  mounted() {
    // 确保初始消息显示后滚动到底部
    this.$nextTick(() => {
      const container = this.$refs.historyContainer;
      container.scrollTop = container.scrollHeight;
    });
  }
}
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 8px;
  animation: fadeIn 0.3s;
}

.message.user {
  background-color: #e3f2fd;
  margin-left: 20%;
}

.message.assistant {
  background-color: #f5f5f5;
  margin-right: 20%;
}

.message-header {
  font-weight: bold;
  margin-bottom: 5px;
  color: #555;
}

.message-content {
  line-height: 1.5;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  min-height: 60px;
  font-family: inherit;
}

.chat-input textarea:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

.send-button {
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0 20px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #349e6e;
}

.send-button:disabled {
  background-color: #a0d9bb;
  cursor: not-allowed;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}

/* 加载动画 */
.dot-flashing {
  position: relative;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #42b983;
  color: #42b983;
  animation: dotFlashing 1s infinite linear alternate;
  animation-delay: 0.5s;
}

.dot-flashing::before, .dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
}

.dot-flashing::before {
  left: -15px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #42b983;
  color: #42b983;
  animation: dotFlashing 1s infinite alternate;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 15px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #42b983;
  color: #42b983;
  animation: dotFlashing 1s infinite alternate;
  animation-delay: 1s;
}

@keyframes dotFlashing {
  0% { background-color: #42b983; }
  50%, 100% { background-color: #c8e6d3; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>