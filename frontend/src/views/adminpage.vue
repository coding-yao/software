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
                <a href="#" class="nav-link" @click="jumptofigures()">
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
            <li class="nav-item">
                <a href="#" class="nav-link" @click="jumpTo('model')">
                <span class="nav-text" v-show="sidebarExpanded">模型管理</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" @click="jumpToApiKeys">
                <span class="nav-text" v-show="sidebarExpanded">API密钥管理</span>
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

            <!-- 模型管理区域 -->
    <div class="model-management-container" v-if="currentPage === 'model'">
        <h1 class="page-title">鱼类体长预测模型管理</h1>
        
        <div class="model-info">
            <div class="info-card">
                <h3>模型状态</h3>
                <div v-if="modelStatus === 'loading'" class="loading-indicator">
                    <span>加载中...</span>
                </div>
                <div v-else>
                    <p v-if="modelStatus === 'ready'">
                        <span class="status-badge success">已加载</span>
                    </p>
                    <p v-else-if="modelStatus === 'uninitialized'">
                        <span class="status-badge warning">未初始化</span>
                    </p>
                    <p v-else>
                        <span class="status-badge error">错误</span>
                    </p>
                    <p v-if="modelInfo.last_trained">
                        最后训练时间: {{ formatDate(modelInfo.last_trained) }}
                    </p>
                    <p v-else>未训练过模型</p>
                </div>
            </div>
            
            <div class="info-card">
                <h3>训练数据统计</h3>
                <p>可用样本数: {{ modelInfo.sample_count || 0 }}</p>
                <p>鱼种数量: {{ modelInfo.species_count || 0 }}</p>
            </div>
        </div>
        
        <div class="model-controls">
                <button 
                    class="train-button" 
                    @click="trainModel" 
                    :disabled="isTraining"
                >
                    <span v-if="!isTraining">训练模型</span>
                    <span v-else>训练中...</span>
                </button>
                
                <div v-if="trainingResult" class="result-card">
                    <h3>训练结果</h3>
                    <p v-if="trainingResult.message">{{ trainingResult.message }}</p>
                    <p v-if="trainingResult.mae_full">
                        完整模型平均绝对误差: {{ trainingResult.mae_full.toFixed(2) }} cm
                    </p>
                    <p v-if="trainingResult.mae_weight">
                        仅体重模型平均绝对误差: {{ trainingResult.mae_weight.toFixed(2) }} cm
                    </p>
                </div>
                
                <div v-if="trainingError" class="error-card">
                    <h3>训练失败</h3>
                    <p>{{ trainingError }}</p>
                </div>
            </div>
        </div>

    <!-- API密钥管理页面 -->
            <div v-if="currentPage === 'api-keys'" class="api-keys-container">
                <h1 class="page-title">API密钥管理</h1>
                
                <div class="key-form">
                    <div class="form-group">
                        <label>选择服务:</label>
                        <select v-model="currentService">
                            <option value="DEEPSEEK">DeepSeek</option>
                            <option value="GLM">GLM-4V</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>API密钥:</label>
                        <input 
                            type="password" 
                            v-model="currentKey" 
                            placeholder="输入API密钥"
                            @input="clearMessages"
                        >
                    </div>
                    
                    <button 
                        class="save-button" 
                        @click="saveKey"
                        :disabled="isSaving"
                    >
                        <span v-if="!isSaving">保存密钥</span>
                        <span v-else>保存中...</span>
                    </button>
                </div>
                
                <div v-if="message" class="message" :class="messageClass">{{ message }}</div>
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
            currentPage: 'users', // 默认为用户管理页面
            // 模型管理相关状态
            modelStatus: 'loading', // loading, ready, uninitialized, error
            modelInfo: {},
            isTraining: false,
            trainingResult: null,
            trainingError: null,
            // API密钥管理相关数据
            currentService: 'DEEPSEEK',
            currentKey: '',
            isSaving: false,
            message: '',
            messageClass: ''
        };
    },
    mounted() {
        this.get_user_list(); //立即执行获取用户列表功能
        this.fetchModelStatus(); // 获取模型状态
    },
    methods: {
        expandSidebar() {
            this.sidebarExpanded = true;
        }, 
        collapseSidebar() {
            this.sidebarExpanded = false;
        },
        jumptofigures(){
          this.$router.push("/underwater");// 导航到首页
        },
        jumpToApiKeys() {
            this.currentPage = 'api-keys';
            this.fetchApiKeys();
        },
        // 获取API密钥
        async fetchApiKeys() {
            try {
                const accessToken = localStorage.getItem('accesstoken');
                const response = await axios.get(
                    'http://localhost:8000/api/keys/',
                    {
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                        }
                    }
                );
                
                // 设置当前密钥
                if (response.data.DEEPSEEK) {
                    this.deepseekKey = response.data.DEEPSEEK;
                    if (this.currentService === 'DEEPSEEK') {
                        this.currentKey = this.deepseekKey;
                    }
                }
                if (response.data.GLM) {
                    this.glmKey = response.data.GLM;
                    if (this.currentService === 'GLM') {
                        this.currentKey = this.glmKey;
                    }
                }
                
            } catch (error) {
                console.error('获取API密钥失败:', error);
                this.showMessage('获取API密钥失败: ' + (error.response?.data?.error || error.message), 'error');
            }
        },
        
        // 保存API密钥
        async saveKey() {
            if (!this.currentKey) {
                this.showMessage('请输入API密钥', 'error');
                return;
            }
            
            this.isSaving = true;
            this.message = '';
            
            try {
                const accessToken = localStorage.getItem('accesstoken');
                const response = await axios.post(
                    'http://localhost:8000/api/AI/keys/',
                    {
                        service: this.currentService,
                        key: this.currentKey
                    },
                    {
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                        }
                    }
                );
                
                this.showMessage(`密钥已${response.data.status === 'created' ? '创建' : '更新'}！`, 'success');
                
                // 更新本地存储的密钥
                if (this.currentService === 'DEEPSEEK') {
                    this.deepseekKey = this.currentKey;
                } else {
                    this.glmKey = this.currentKey;
                }
                
            } catch (error) {
                console.error('保存API密钥失败:', error);
                this.showMessage('保存失败: ' + (error.response?.data?.error || error.message), 'error');
            } finally {
                this.isSaving = false;
            }
        },
        
        // 显示消息
        showMessage(text, type) {
            this.message = text;
            this.messageClass = type;
            
            // 5秒后自动清除消息
            setTimeout(() => {
                this.message = '';
            }, 5000);
        },
        
        // 清除消息
        clearMessages() {
            this.message = '';
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
        },

        jumpTo(page) {
            this.currentPage = page;
            
            // 如果是模型管理页面，刷新模型状态
            if (page === 'model') {
                this.fetchModelStatus();
            }
        },

        // 获取模型状态
        async fetchModelStatus() {
            this.modelStatus = 'loading';
            try {
                const accessToken = localStorage.getItem('accesstoken');
                const response = await axios.get(
                    'http://localhost:8000/api/AI/model-status/',
                    {
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                        }
                    }
                );
                
                this.modelInfo = response.data;
                this.modelStatus = response.data.status || 'ready';
            } catch (error) {
                console.error('获取模型状态失败:', error);
                this.modelStatus = 'error';
                this.modelInfo = {};
            }
        },
        
        // 训练模型
        async trainModel() {
            this.isTraining = true;
            this.trainingResult = null;
            this.trainingError = null;
            
            try {
                const accessToken = localStorage.getItem('accesstoken');
                const response = await axios.post(
                    'http://localhost:8000/api/AI/train-models/',
                    {},
                    {
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                        }
                    }
                );
                
                this.trainingResult = response.data;
                // 刷新模型状态
                await this.fetchModelStatus();
            } catch (error) {
                console.error('训练模型失败:', error);
                if (error.response) {
                    this.trainingError = error.response.data.error || '训练失败';
                } else {
                    this.trainingError = error.message || '训练失败';
                }
            } finally {
                this.isTraining = false;
            }
        },


    }  //end methods
} // end export

</script>

<style scoped>
/* API密钥管理容器样式 */
.api-keys-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 30px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.key-form {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
}

.form-group select, 
.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group select:focus, 
.form-group input:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.save-button {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 25px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  display: block;
  width: 100%;
  margin-top: 10px;
}

.save-button:hover:not(:disabled) {
  background-color: #2980b9;
}

.save-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 6px;
  font-size: 16px;
  text-align: center;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 调整侧边栏导航项样式 */
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

/* 模型管理容器 */
.model-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 模型信息卡片 */
.model-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.info-card h3 {
  margin-top: 0;
  color: #2d3748;
  border-bottom: 2px solid #f0f4f8;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge.success {
  background-color: #c6f6d5;
  color: #2f855a;
}

.status-badge.warning {
  background-color: #feebc8;
  color: #b7791f;
}

.status-badge.error {
  background-color: #fed7d7;
  color: #c53030;
}

/* 模型控制区域 */
.model-controls {
  background: #ffffff;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.train-button {
  background-color: #3182ce;
  color: white;
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.train-button:hover:not(:disabled) {
  background-color: #2b6cb0;
}

.train-button:disabled {
  background-color: #cbd5e0;
  cursor: not-allowed;
}

/* 结果卡片 */
.result-card {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0fff4;
  border-radius: 6px;
  border: 1px solid #c6f6d5;
}

.result-card h3 {
  margin-top: 0;
  color: #2f855a;
}

/* 错误卡片 */
.error-card {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff5f5;
  border-radius: 6px;
  border: 1px solid #fed7d7;
}

.error-card h3 {
  margin-top: 0;
  color: #c53030;
}

/* 加载指示器 */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  color: #3182ce;
}

.loading-indicator::after {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid rgba(49, 130, 206, 0.3);
  border-radius: 50%;
  border-top-color: #3182ce;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}

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