import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../redux/store';
import { 
  login, 
  register, 
  logout, 
  getCurrentUser, 
  clearError 
} from '../redux/slices/authSlice';
import { 
  LoginRequest, 
  UserCreate 
} from '../types/user';

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user, token, isAuthenticated, loading, error } = useSelector(
    (state: RootState) => state.auth
  );

  // 登录
  const loginUser = useCallback(
    (credentials: LoginRequest) => {
      return dispatch(login(credentials));
    },
    [dispatch]
  );

  // 注册
  const registerUser = useCallback(
    (userData: UserCreate) => {
      return dispatch(register(userData));
    },
    [dispatch]
  );

  // 登出
  const logoutUser = useCallback(() => {
    dispatch(logout());
  }, [dispatch]);

  // 获取当前用户信息
  const fetchCurrentUser = useCallback(() => {
    return dispatch(getCurrentUser());
  }, [dispatch]);

  // 清除错误
  const clearAuthError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  return {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    loginUser,
    registerUser,
    logoutUser,
    fetchCurrentUser,
    clearAuthError,
  };
}; 