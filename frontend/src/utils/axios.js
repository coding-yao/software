// src/utils/axios.js
import axios from "axios";

const new_axios = axios.create();

// 请求拦截器：自动添加 Token 到请求头
new_axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("accesstoken");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 响应拦截器：处理 Token 过期
new_axios.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // 检测到 Token 过期（状态码 401）且未重试过
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // 尝试刷新 Token
                const refreshToken = localStorage.getItem("refresh_token");
                const response = await axios.post("http://localhost:8000/api/user/access/", { refresh: refreshToken });

                const { access_token, refresh_token } = response.data;
                localStorage.setItem("access_token", access_token);
                localStorage.setItem("refresh_token", refresh_token);

                // 重试原始请求
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return new_axios(originalRequest);
            } catch (refreshError) {
                // 刷新 Token 失败：清除存储并跳转登录
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                window.location.href = "/login";
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default new_axios;