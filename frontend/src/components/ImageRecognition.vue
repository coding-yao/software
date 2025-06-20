<template>
  <div class="image-recognition">
    <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop="handleDrop">
      <div v-if="!imagePreview" class="upload-prompt">
        <i class="upload-icon">📁</i>
        <p>点击或拖拽图片到此处</p>
        <p class="hint">支持 JPG, PNG 格式，最大 5MB</p>
      </div>
      <img v-else :src="imagePreview" alt="预览" class="preview-image" />
      <input type="file" accept="image/*" @change="handleUpload" ref="fileInput" class="file-input" />
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>AI正在分析图片内容...</p>
    </div>
    
    <div v-if="result" class="result">
      <h3>识别结果：</h3>
      <p>{{ result }}</p>
    </div>
    
    <div v-if="error" class="error">
      <i class="error-icon">⚠️</i>
      <p>{{ error }}</p>
    </div>
    
    <button v-if="imagePreview" @click="clearAll" class="clear-btn">
      清除
    </button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      imagePreview: null,
      result: null,
      error: null,
      loading: false
    };
  },
  methods: {
    triggerUpload() {
      this.$refs.fileInput.click();
    },
    
    handleDrop(e) {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) this.processFile(file);
    },
    
    async handleUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      this.processFile(file);
    },
    
    async processFile(file) {
      // 验证文件类型和大小
      if (!file.type.match('image.*')) {
        this.error = '请上传图片文件 (JPG, PNG 等)';
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) {
        this.error = '图片大小不能超过 5MB';
        return;
      }
      
      // 重置状态
      this.result = null;
      this.error = null;
      this.loading = true;
      
      // 预览图片
      this.imagePreview = URL.createObjectURL(file);
      
      // 创建FormData
      const formData = new FormData();
      formData.append('image', file);
      
      try {
        // 发送到Django后端
        const response = await axios.post(
          'http://localhost:8000/api/AI/recognize-image/', 
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 30000  // 30秒超时
          }
        );
        
        this.result = response.data.result;
      } catch (err) {
        this.error = '识别失败: ' + (err.response?.data?.error || err.message || '服务器错误');
      } finally {
        this.loading = false;
      }
    },
    
    clearAll() {
      this.imagePreview = null;
      this.result = null;
      this.error = null;
      this.$refs.fileInput.value = null;
    }
  }
}
</script>

<style scoped>
.image-recognition {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #f9fafb;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #3b82f6;
  background-color: #f0f9ff;
}

.upload-prompt {
  color: #6b7280;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.hint {
  font-size: 0.9rem;
  margin-top: 8px;
  color: #9ca3af;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.file-input {
  display: none;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #4b5563;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result {
  background-color: #f0fdf4;
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid #10b981;
}

.result h3 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #047857;
}

.error {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fef2f2;
  border-radius: 12px;
  padding: 16px;
  color: #b91c1c;
  border-left: 4px solid #ef4444;
}

.error-icon {
  font-size: 24px;
}

.clear-btn {
  align-self: flex-end;
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background-color: #fee2e2;
}
</style>