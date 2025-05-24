<template>
    <div class="sidebar-container">
        <!-- 侧边栏主体 -->
        <aside 
        class="sidebar" 
        :class="{ 'sidebar-expanded': sidebarExpanded }"
        @mouseenter="expandSidebar"
        @mouseleave="collapseSidebar"
        >

        <div class="sidebar-header">
            <h2 class="logo-text" v-show="sidebarExpanded">海洋牧场管理员界面</h2>
        </div>
        
        <div class="user-info" v-show="sidebarExpanded">
            <div class="user-details">
            <p class="user-name">欢迎，管理员</p>
            </div>
        </div>
        
        <nav class="sidebar-nav">
            <ul>
            <li class="nav-item">
                <a href="#" class="nav-link" @click="jumpTo('dashboard')">
                <span class="nav-text" v-show="sidebarExpanded">可视化界面</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" @click="jumpTo('users')">
                <span class="nav-text" v-show="sidebarExpanded">用户管理</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" @click="jumpTo('settings')">
                <span class="nav-text" v-show="sidebarExpanded">设备信息</span>
                </a>
            </li>
            </ul>
        </nav>
        
        <div class="sidebar-toggle" v-show="!sidebarExpanded">
            <i class="toggle-icon">▶️</i>
        </div>
        </aside>
        
        <!-- 主内容区域 -->
        <main class="main-content" :class="{ 'sidebar-expanded-content': sidebarExpanded }">
            <div class="user-list-container">
                <h1 class="page-title">用户列表</h1>
                <!-- 列表内容 -->
                <div class="user-table">
                    <table>
                        <thead>
                        <tr>
                            <th>用户ID</th>
                            <th>账号</th>
                            <th>角色</th>
                            <th>创建时间</th>
                            <th>状态</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="user in user_list" :key="user.user_id" class="user-row">
                            <td>{{ user.user_id }}</td>
                            <td>{{ user.account }}</td>
                            <td>{{ user.role }}</td>
                            <td>{{ formatDate(user.create_time) }}</td>
                            <td>
                            <span class="status-badge" :class="{ 'approved': user.is_active, 'pending': !user.is_approved }">
                                {{ user.is_active ? '已批准' : '待审核' }}
                            </span>
                            </td>
                            <td>
                                <!-- 仅当 is_active 为 false 或 0 时显示按钮 -->
                                <button 
                                v-if="!user.is_active" 
                                class="action-button" 
                                @click="approve(user.user_id)"
                                >
                                通过
                                </button>
                                <button 
                                v-else
                                class="action-button" 
                                @click="display(user.user_id)"
                                >
                                修改信息
                                </button>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div><!--end user-list-container-->


            <!--修改用户信息时候的输入框-->
            <div  v-if="isModalOpen"  class="modal-overlay">
                <div class="modal-content">
                    <!-- 输入框1 -->
                    <div class="input-group">
                        <input type="text" placeholder="输入新账户名称" ref="newaccount">
                    </div>
                    <!-- 输入框2 -->
                    <div class="input-group">
                        <input type="text" placeholder="输入新密码" ref="newpassword">
                    </div>
                    <!-- 选择框 -->
                    <div class="input-group">
                        <select ref="new_role">
                        <option value="">选择用户身份</option>
                        <option value="viewer">游客</option>
                        <option value="fisher">渔民</option>
                        <option value="admin">管理员</option>
                        </select>
                    </div>
                    <button @click="notdisplay()">取消</button>
                    <button @click="update()">提交</button>
                </div>
            </div>


        </main>
    </div>
</template>

<script>
import axios from 'axios';
import new_axios from '@/utils/axios';// 用于捕获401错误进行刷新的axios通信组件 暂时没用上

export default {
    data() {
        return {
            user_list:[],
            sidebarExpanded: false,
            isModalOpen:false,
            choosed_user_id: 0,
        };
    },
    mounted() {
        this.get_user_list(); //立即执行获取用户列表功能
    },
    methods: {
        expandSidebar() {
            this.sidebarExpanded = true;
        }, 
        collapseSidebar() {
            this.sidebarExpanded = false;
        },
        get_user_list() {
            const accessToken = localStorage.getItem('accesstoken');
            console.log(accessToken);
            const url = `http://localhost:8000/api/user/list/`;
            axios
            .get(url,
                {
                    headers: {
                        // 'Www-Authenticate': `Bearer ${accessToken}`,
                        'Authorization': `Bearer ${accessToken}`,
                    },
                }
            )
            .then(response => {
                // 请求成功
                this.user_list = response.data.user_list;
                console.log('用户列表:', this.user_list[0]);
            })
            .catch(error => {
                // 处理错误
                if (error.response) {
                    switch (error.response.status) {
                        case 401:
                            console.error('Token 无效或过期');
                            break;
                        case 403:
                            console.error('权限不足：非管理员用户');
                            break;
                        default:
                            console.error('请求失败:', error.response.data);
                    }
                } else {
                    console.error('网络错误:', error.message);
                }
            });
        },//end get user list
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString();
        },
        approve(user_id){
            const data = {};
            const accessToken = localStorage.getItem('accesstoken');
            axios
            .put(
                `http://localhost:8000/api/user/approve/${user_id}/`, 
                data,
                {
                    headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    }
                }
            )
            .then((response) => {   // 接收后端发来的response 或error
                console.log(response);
                this.get_user_list();
            })
        },
        display(user_id){
            this.isModalOpen = true;
            this.choosed_user_id = user_id;
        },
        notdisplay(){
            this.isModalOpen = false;
        },
        update(){
            const new_account = this.$refs['newaccount'].value; 
            const new_password = this.$refs['newpassword'].value;
            const new_role = this.$refs['new_role'].value;
            const accessToken = localStorage.getItem('accesstoken');
            const new_userdata = { // 构建要发送到后端的数据信息
                account: new_account,
                password: new_password,
                role: new_role,
            };
            axios
            .put(
                `http://localhost:8000/api/user/update/${this.choosed_user_id}/`, 
                new_userdata,
                {
                    headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    }
                }
            )
            .then((response) => {   // 接收后端发来的response 或error
                console.log(response);
                this.isModalOpen = false;
                this.get_user_list();
            })
        }


    }  //end methods
} // end export

</script>

<style scoped>
/*表格样式*/
.user-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.page-title {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #3b82f6;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.user-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

th {
  background-color: #f1f5f9;
  font-weight: 600;
}

.sidebar-container {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏样式 */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: 60px; /* 收起状态宽度 */
  background-color: #1e293b;
  color: white;
  transition: width 0.3s ease;
  z-index: 100;
  overflow: hidden;
}

.sidebar-expanded {
  width: 240px; /* 展开状态宽度 */
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 16px;
  height: 60px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 24px;
  margin-right: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-right: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
}

.sidebar-nav {
  padding: 10px 0;
}

.nav-item {
  list-style: none;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-link:hover {
  background-color: #334155;
  color: white;
}

.nav-icon {
  font-size: 18px;
  width: 30px;
}

.nav-text {
  margin-left: 12px;
  white-space: nowrap;
}

.sidebar-toggle {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 30px;
  background-color: #334155;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  margin-left: 60px; /* 初始边距等于收起的侧边栏宽度 */
  transition: margin-left 0.3s ease;
  padding: 20px;
}

.sidebar-expanded-content {
  margin-left: 240px; /* 侧边栏展开时的边距 */
}

/* ————————————————————————————————改变用户信息的输入框样式 */
/* 覆盖层样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5); /* 半透明黑色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

/* 内容容器 */
.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
}

/* 输入组样式 */
.input-group {
  margin-bottom: 16px;
}

.input-group label {
  display: block;
  margin-bottom: 6px;
  color: #666;
  font-size: 14px;
}

.input-group input,
.input-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.input-group select {
  appearance: none;
  background: white url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e") right 8px center no-repeat;
  background-size: 16px;
  padding-right: 32px;
}


</style>