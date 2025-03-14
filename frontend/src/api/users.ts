import api from './axios';
import { User, UserUpdate } from '../types/user';

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await api.get<User>('/users/me');
    return response.data;
  } catch (error) {
    console.error('Error fetching current user:', error);
    throw error;
  }
};

// 更新用户资料
export const updateUserProfile = async (data: UserUpdate): Promise<User> => {
  try {
    const response = await api.put<User>('/users/me', data);
    return response.data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

// 获取指定用户信息
export const getUserById = async (userId: string): Promise<User> => {
  try {
    const response = await api.get<User>(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching user ${userId}:`, error);
    throw error;
  }
}; 