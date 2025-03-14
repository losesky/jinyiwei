import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface PublicRouteProps {
  children: React.ReactNode;
  restricted?: boolean;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ 
  children, 
  restricted = false 
}) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  
  // 添加调试信息
  useEffect(() => {
    console.log('PublicRoute: path =', location.pathname);
    console.log('PublicRoute: isAuthenticated =', isAuthenticated);
    console.log('PublicRoute: restricted =', restricted);
    
    if (restricted && isAuthenticated) {
      const from = location.state?.from?.pathname || '/';
      console.log('PublicRoute: Redirecting to', from);
    }
  }, [isAuthenticated, restricted, location]);
  
  // 如果路由是受限的（如登录、注册页面）且用户已登录，重定向到首页或来源页面
  if (restricted && isAuthenticated) {
    const from = location.state?.from?.pathname || '/';
    return <Navigate to={from} replace />;
  }

  // 否则，渲染子组件
  return <>{children}</>;
};

export default PublicRoute; 