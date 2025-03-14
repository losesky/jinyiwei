import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 15000, // 增加请求超时时间
  withCredentials: false, // 跨域请求不携带凭证
});

console.log('Axios instance created with baseURL:', api.defaults.baseURL);
console.log('Axios withCredentials:', api.defaults.withCredentials);

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    console.log('Request interceptor: token =', token ? `${token.substring(0, 20)}...` : 'null');
    
    // 如果有token，则添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Request interceptor: Added Authorization header');
    } else {
      console.log('Request interceptor: No token found');
    }
    
    console.log('Request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data ? (typeof config.data === 'string' ? config.data : JSON.stringify(config.data)) : null,
      withCredentials: config.withCredentials
    });
    
    // 确保OPTIONS请求不携带Authorization头
    if (config.method?.toUpperCase() === 'OPTIONS') {
      delete config.headers.Authorization;
      console.log('Request interceptor: Removed Authorization header for OPTIONS request');
    }
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('Response:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    if (error.response) {
      console.error('Error response:', {
        status: error.response.status,
        statusText: error.response.statusText,
        headers: error.response.headers,
        data: error.response.data
      });
    }
    
    // 处理401错误（未授权）
    if (error.response && error.response.status === 401) {
      // 清除token
      localStorage.removeItem('token');
      // 重定向到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api; 