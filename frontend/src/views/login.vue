<template>
    <div class="container">
        <h1 class="title">海洋牧场管理系统</h1>
        <div v-if="isRegisterView" class="register-box"> <!-- 负责注册的组件框 点击“已有账号去登录”时 会和登录组件框相互切换 -->
            <!-- 后续在注册功能中应该还要再加一些信息 比如选择用户组，个人信息和账号简介等 -->
            <div class="input-box">
                <input type="text" placeholder="用户名" ref="register-username"> <!-- 三个输入框 -->
                <input type="password" placeholder="密码" ref="register-password">
                <input type="password" placeholder="确认密码" ref="register-confirm-password">
                <select ref="register-role">
                    <option value="" disabled selected>选择用户身份</option>
                    <option value="viewer">游客</option>
                    <option value="fisher">渔民</option>
                    <option value="admin">管理员</option>
                </select>
            </div>
            <button class="ok" @click="register()">注册</button> <!-- 注册按钮 点击触发script中的register函数逻辑 -->
            <p class="register-title">
                已有账号，去<button @click="toggleView()">登录</button> <!-- 切换按钮（切换到登录组件框） -->
            </p>
        </div>

        <div v-else class="login-box "> <!-- 负责登录的组件框 -->
            <div class="input-box">
                <input type="text" placeholder="用户名" ref="login-username"> <!-- 两个输入框 -->
                <input type="password" placeholder="密码" ref="login-password">
            </div>
            <button class="ok" @click="login()">登录</button> <!-- 登录按钮 点击触发script中的login函数逻辑 -->
            <p class="login-title">
                没有账号，去<button @click="toggleView()">注册</button> <!-- 切换按钮 -->
            </p>

        </div>
    </div>

</template>

<script>
import axios from 'axios';

export default {
    data() { // data里定义数据
        return {
            isRegisterView: false
        };
    },
    methods: {// methods里定义函数
        toggleView() {//点击 “已有账号去登录” 等切换按钮时， 将isRegisterView变量取反 用于显示不同的组件框
            this.isRegisterView = !this.isRegisterView;
        },
        register() {// 点击注册按钮时触发的函数
            const username = this.$refs['register-username'].value; //这两行从输入框里获取信息 
            const password = this.$refs['register-password'].value;
            const confirmPassword = this.$refs['register-confirm-password'].value;
            const role = this.$refs['register-role'].value;
            console.log(role);
            if (!username || !password || !confirmPassword) {// 对输入的内容进行合法性检验
                alert('请填写完整的用户名、密码和确认密码');
                return;
            }
            if (password !== confirmPassword) {
                alert('密码和确认密码不一致，请重新输入');
                return;
            }
            const regesterdata = { // 构建要发送到后端的数据信息
                account: username,
                password: password,
                role: role,
            };
            const url = `http://localhost:8000/api/user/register/`; // 构建url 发送到后台的/reg这个url 
            axios   // 数据通信的逻辑 调用axios 使用post请求方法发送数据到后端
                .post(url, regesterdata)
                .then((response) => {   // 接收后端发来的response 或error
                    alert(response.data.message);
                })
                .catch((error) => {  // 
                    if (error.response && error.response.data) {
                        alert(error.response.data.error);
                    } else {
                        console.error("注册失败:", error);
                        alert("注册失败:", error);
                    }
                });
        },

        login() {  // 点击登录按钮时触发的函数
            // 登录的逻辑 通信等方式与注册逻辑类似 以下分别是 提取输入框信息 构建要发送到后台的信息 确定要发送到后台的此地址 用axios进行通信
            const username = this.$refs['login-username'].value;
            const password = this.$refs['login-password'].value;
            if (!username || !password) {
                alert('请填写完整的用户名、密码');
                return;
            }
            const logindata = {
                account: username,
                password: password,
            };
            const url = `http://localhost:8000/api/user/login/`;
            axios
                .post(url, logindata)
                .then((response) => {
                    console.log(response.data.access);
                    localStorage.setItem('accesstoken', response.data.access); // Access Token
                    localStorage.setItem('refresh_token', response.data.refresh); // Refresh Token
                    localStorage.setItem('user_id', response.data.user.user_id); // userid
                    localStorage.setItem('user_role', response.data.user.role); // user
                    localStorage.setItem('user_account', response.data.user.account); // user

                    alert(response.data.message); // 显示登录成功的消息
                    if (response.data.user.role == 'admin')
                        this.$router.push("/adminpage"); 
                    else
                        this.$router.push("/underwater");// 导航到首页
                })
                .catch((error) => {
                    if (error.response && error.response.data) {
                        alert(error.response.data.error);
                    } else {
                        // 显示通用错误消息
                        console.error("登录失败:", error);
                        alert("登录失败");
                    }
                });
        }
    }
}

</script>

<style scoped>
/* style为装饰元素 scoped代表只在这一个页面生效*/
/* 对所有页面生效的装饰元素 在assets/main.css中 */
.container {
    position: relative;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh; /* 确保容器至少占满整个视口 */
    gap:20%;
    background-image: url('../assets/bg.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

.title {
  font-family: 'Arial Black', sans-serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  text-align: center;
  color: #ffffff;
  margin: 0.5em 0;
  
  -webkit-text-stroke: 2px rgba(0, 0, 0, 0.2);
  
  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.1),
    0 4px 8px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.1),
    0 16px 32px rgba(0, 0, 0, 0.1),
    0 0 30px rgba(10, 80, 180, 0.5),
    0 0 40px rgba(10, 80, 180, 0.5);
  
}

.register-box,
.login-box {
    background-color: white;
    border-radius: 10px;
    /* 给盒子设置圆角 */
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    /* 添加阴影效果 */
    padding: 20px;
    width: 300px;
    /* 设置一个合适的宽度，可根据需求调整 */
}

/* 输入框区域样式 */
.input-box {
    display: flex;
    flex-direction: column;
    margin-bottom: 15px;
}

.input-box input {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    /* 输入框圆角 */
}

select {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    /* 输入框圆角 */
}

/* 标题样式 */
.register-title,
.login-title {
    text-align: center;
    margin-bottom: 15px;
}
</style>