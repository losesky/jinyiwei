import React from 'react';
import { Routes, Route } from 'react-router-dom';

// 布局
import MainLayout from '../layouts/MainLayout';
import AuthLayout from '../layouts/AuthLayout';

// 页面
import HomePage from '../pages/Home';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '../pages/auth/ResetPasswordPage';
import ChangePasswordPage from '../pages/user/ChangePasswordPage';
import ProfilePage from '../pages/user/ProfilePage';
import AdminPage from '../pages/admin/AdminPage';
import NotFoundPage from '../pages/NotFoundPage';
import UnauthorizedPage from '../pages/UnauthorizedPage';

// 路由守卫
import PrivateRoute from '../components/auth/PrivateRoute';
import PublicRoute from '../components/auth/PublicRoute';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* 主布局路由 */}
      <Route path="/" element={<MainLayout />}>
        {/* 公共页面 */}
        <Route index element={<HomePage />} />
        
        {/* 需要登录的页面 */}
        <Route path="profile" element={
          <PrivateRoute>
            <ProfilePage />
          </PrivateRoute>
        } />
        
        <Route path="change-password" element={
          <PrivateRoute>
            <ChangePasswordPage />
          </PrivateRoute>
        } />
        
        {/* 需要管理员权限的页面 */}
        <Route path="admin" element={
          <PrivateRoute requiredRoles={['admin']}>
            <AdminPage />
          </PrivateRoute>
        } />
        
        {/* 无权限页面 */}
        <Route path="unauthorized" element={<UnauthorizedPage />} />
        
        {/* 404页面 */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
      
      {/* 认证布局路由 */}
      <Route path="/" element={<AuthLayout />}>
        {/* 登录页面 */}
        <Route path="login" element={
          <PublicRoute restricted>
            <LoginPage />
          </PublicRoute>
        } />
        
        {/* 注册页面 */}
        <Route path="register" element={
          <PublicRoute restricted>
            <RegisterPage />
          </PublicRoute>
        } />
        
        {/* 忘记密码页面 */}
        <Route path="forgot-password" element={
          <PublicRoute restricted>
            <ForgotPasswordPage />
          </PublicRoute>
        } />
        
        {/* 重置密码页面 */}
        <Route path="reset-password" element={
          <PublicRoute restricted>
            <ResetPasswordPage />
          </PublicRoute>
        } />
      </Route>
    </Routes>
  );
};

export default AppRoutes; 