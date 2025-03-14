import api from './axios';
import { 
  LoginRequest, 
  LoginResponse, 
  UserCreate, 
  User, 
  PasswordResetRequest, 
  PasswordResetConfirm, 
  PasswordChange, 
  MessageResponse 
} from '../types/user';

// 登录
export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  // 使用URLSearchParams格式，符合OAuth2规范
  const formData = new URLSearchParams();
  formData.append('username', data.username);
  formData.append('password', data.password);
  formData.append('grant_type', 'password');  // OAuth2 要求

  try {
    console.log('Login request data:', {
      username: data.username,
      password: '******', // 不记录实际密码
      grant_type: 'password'
    });
    console.log('Request headers:', {
      'Content-Type': 'application/x-www-form-urlencoded'
    });
    console.log('Request body (form data):', formData.toString());
    
    const response = await api.post<LoginResponse>('/auth/login', formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    console.log('Login response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Login error:', error);
    console.error('Error response:', error.response?.data);
    console.error('Error status:', error.response?.status);
    console.error('Error headers:', error.response?.headers);
    throw error;
  }
};

// 注册
export const register = async (data: UserCreate): Promise<User> => {
  try {
    console.log('Registration request data:', {
      ...data,
      password: '******' // 不记录实际密码
    });
    
    // 确保full_name不是空字符串
    const userData = {
      ...data,
      full_name: data.full_name?.trim() || undefined
    };
    
    console.log('Processed registration data:', {
      ...userData,
      password: '******' // 不记录实际密码
    });
    
    const response = await api.post<User>('/auth/register', userData);
    console.log('Registration response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Registration error:', error);
    console.error('Error response:', error.response?.data);
    console.error('Error status:', error.response?.status);
    console.error('Error headers:', error.response?.headers);
    throw error;
  }
};

// 请求密码重置
export const requestPasswordReset = async (data: PasswordResetRequest): Promise<MessageResponse> => {
  const response = await api.post<MessageResponse>('/auth/password-reset/request', data);
  return response.data;
};

// 确认密码重置
export const confirmPasswordReset = async (data: PasswordResetConfirm): Promise<MessageResponse> => {
  const response = await api.post<MessageResponse>('/auth/password-reset/confirm', data);
  return response.data;
};

// 修改密码
export const changePassword = async (data: PasswordChange): Promise<MessageResponse> => {
  const response = await api.post<MessageResponse>('/auth/password-change', data);
  return response.data;
}; 