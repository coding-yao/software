<template>
    <div class="container">
        <div v-if="isRegisterView" class="register-box"> <!-- 负责注册的组件框 点击“已有账号去登录”时 会和登录组件框相互切换 -->
            <!-- 后续在注册功能中应该还要再加一些信息 比如选择用户组，个人信息和账号简介等 -->
            <div class="input-box">
                <input type="text" placeholder="用户名" ref="register-username"> <!-- 三个输入框 -->
                <input type="password" placeholder="密码" ref="register-password">
                <input type="password" placeholder="确认密码" ref="register-confirm-password">
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
    <button class="ok" @click="idle()">跳转</button> <!--暂时加的 在页面底端 目前没用-->

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
            if (!username || !password || !confirmPassword) {// 对输入的内容进行合法性检验
                alert('请填写完整的用户名、密码和确认密码');
                return;
            }
            if (password !== confirmPassword) {
                alert('密码和确认密码不一致，请重新输入');
                return;
            }
            const regesterdata = { // 构建要发送到后端的数据信息
                type: 0,//0代表注册信息 这是因为此时注册和登录都是发送到/reg这个url 要通过type来标识是注册还是登录信息
                // 我们后续可以把注册和登录的逻辑分开 发送到不同的url从而用不同函数处理
                username: username,
                password: password,
            };
            const url = `http://localhost:5000/reg`; // 构建url 发送到后台的/reg这个url 
            axios   // 数据通信的逻辑 调用axios 使用post请求方法发送数据到后端
                // 我们在后端代码中使用Django的相关逻辑接收此post请求即可 我之前也没用过 刚刚在问ai
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
                type: 1,//1为登录信息
                username: username,
                password: password,
            };
            const url = `http://localhost:5000/reg`;
            axios
                .post(url, logindata)
                .then((response) => {
                    alert(response.data.message); // 显示登录成功的消息
                    this.$router.push("/home"); // 导航到首页
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
    background-color: #f4f4f4;
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

/* 标题样式 */
.register-title,
.login-title {
    text-align: center;
    margin-bottom: 15px;
}
</style>