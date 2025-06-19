<template>
  <div class="header">
    <div class="left-buttons">
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

    <div class="title">海洋牧场 数据可视化页面</div>

    <div class="right-info">
      <span>欢迎，{{ userrole }} : {{ useraccount }}</span>
      <span>{{ currentDateTime }}</span>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

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
      currentDateTime: '',
      userrole: '',
      useraccount: '',
    };
  },
  mounted() {
    this.updateDateTime();
    setInterval(this.updateDateTime, 1000);
    this.getuser();
  },
  methods: {
    updateDateTime() {
      const now = new Date();
      const date = now.toLocaleDateString();
      const time = now.toLocaleTimeString();
      this.currentDateTime = `${date} ${time}`;
    },
    getuser(){
      this.userrole = localStorage.getItem("user_role");
      this.useraccount = localStorage.getItem("user_account");

      if (this.userrole === 'viewer') {
        this.userrole = '游客';
      }
      else if (this.userrole === 'fisher') {
        this.userrole = '渔民';
      }
      else if (this.userrole === 'admin') {
        this.userrole = '管理员';
      }
    },
    fisher_register(){
      const accessToken = localStorage.getItem('accesstoken');
      console.log(accessToken);
      const data = {};
      axios
      .post(
          `http://localhost:8000/api/user/register_fisher/`, 
          data,
          {
              headers: {
              'Authorization': `Bearer ${accessToken}`,
              }
          }
      )
      .then((response) => {   // 接收后端发来的response 或error
          console.log(response);
      })
    },
  }
}
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
}

.left-buttons {
  display: flex;
  gap: 0.6rem;
  margin-left: 20px;
}

.title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.2rem;
  font-weight: bold;
  white-space: nowrap;
}

.right-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-right: 20px;
}

.nav-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #f0f0f0;
  cursor: pointer;
  white-space: nowrap;
}

.nav-btn:hover {
  background: #e0e0e0;
}

.nav-btn.active {
  background: #1890ff;
  color: white;
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