<template>
  <div class="header">
    <div class="head-links">
      <button 
        class="nav-btn" 
        :class="{ active: currentPage === 'main' }"
        @click="$router.push('/main')"
      >主要信息</button>
      <button 
        class="nav-btn" 
        :class="{ active: currentPage === 'underwater' }"
        @click="$router.push('/underwater')"
      >水下系统</button>
      <button 
        class="nav-btn" 
        :class="{ active: currentPage === 'smarthub' }"
        @click="$router.push('/smarthub')"
      >智能中心</button>
    </div>
    <div class="title-container">
      <p class='headtext'>海洋牧场 数据可视化页面</p>
    </div>
    <div class="date-time">
      {{ currentDateTime }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'NavBar',
  props: {
    currentPage: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      currentDateTime: ''
    };
  },
  mounted() {
    this.updateDateTime();
    setInterval(this.updateDateTime, 1000);
  },
  methods: {
    updateDateTime() {
      const now = new Date();
      // 使用更简洁的时间格式
      this.currentDateTime = now.toLocaleTimeString() + '   ' + now.toLocaleDateString();
    }
  }
}
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #fff;
  padding: 0.8rem 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  z-index: 1000;
  gap: 1rem;
  box-sizing: border-box;
}

.head-links {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
  flex-wrap: wrap;
  min-width: 0;
}

.title-container {
  text-align: center;
  min-width: 0;
}

.headtext {
  margin: 0;
  font-size: clamp(1rem, 2vw, 1.2rem);
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  background-color: #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: clamp(0.8rem, 1.5vw, 1rem);
  white-space: nowrap;
}

.nav-btn:hover {
  background-color: #e0e0e0;
}

.nav-btn.active {
  background-color: #1890ff;
  color: white;
}

.date-time {
  font-size: clamp(0.8rem, 1.5vw, 1rem);
  color: #666;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

@media (max-width: 768px) {
  .header {
    grid-template-columns: auto auto auto;
    padding: 0.5rem;
    gap: 0.5rem;
  }
  
  .nav-btn {
    padding: 0.3rem 0.6rem;
  }
  
  .headtext {
    font-size: 0.9rem;
  }
  
  .date-time {
    font-size: 0.7rem;
  }
}
</style>