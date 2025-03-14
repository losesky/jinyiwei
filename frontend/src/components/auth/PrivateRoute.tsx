import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../../hooks/useAuth';

interface PrivateRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ 
  children, 
  requiredRoles = [] 
}) => {
  const { isAuthenticated, user, loading, fetchCurrentUser } = useAuth();
  const location = useLocation();

  // 如果有token但没有用户信息，获取用户信息
  useEffect(() => {
    console.log('PrivateRoute: path =', location.pathname);
    console.log('PrivateRoute: isAuthenticated =', isAuthenticated);
    console.log('PrivateRoute: user =', user);
    console.log('PrivateRoute: loading =', loading);
    
    if (isAuthenticated && !user && !loading) {
      console.log('PrivateRoute: Fetching user info');
      fetchCurrentUser();
    }
    
    if (!isAuthenticated) {
      console.log('PrivateRoute: Redirecting to login');
    }
  }, [isAuthenticated, user, loading, fetchCurrentUser, location]);

  // 如果正在加载，显示加载中
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 'calc(100vh - 64px)' 
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  // 如果未登录，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果需要特定角色但用户没有该角色，重定向到无权限页面
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some(role => {
      if (role === 'admin' && user?.is_superuser) {
        return true;
      }
      // 这里可以添加更多角色判断逻辑
      return false;
    });

    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // 通过所有检查，渲染子组件
  return <>{children}</>;
};

export default PrivateRoute; 