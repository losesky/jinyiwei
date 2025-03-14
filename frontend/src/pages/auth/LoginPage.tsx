import React, { useEffect } from 'react';
import { Card, Alert } from 'antd';
import { useLocation } from 'react-router-dom';
import LoginForm from '../../components/auth/LoginForm';

interface LocationState {
  registered?: boolean;
  passwordReset?: boolean;
}

const LoginPage: React.FC = () => {
  const location = useLocation();
  const state = location.state as LocationState;
  
  // 清除location state，防止刷新后仍然显示提示
  useEffect(() => {
    if (state?.registered || state?.passwordReset) {
      window.history.replaceState({}, document.title);
    }
  }, [state]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: 'calc(100vh - 64px)',
      padding: '20px',
      background: '#f0f2f5'
    }}>
      <Card 
        style={{ 
          width: '100%', 
          maxWidth: 450,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}
        bordered={false}
      >
        {state?.registered && (
          <Alert
            message="注册成功"
            description="您已成功注册，请使用您的账号和密码登录。"
            type="success"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}
        
        {state?.passwordReset && (
          <Alert
            message="密码重置成功"
            description="您的密码已成功重置，请使用新密码登录。"
            type="success"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}
        
        <LoginForm />
      </Card>
    </div>
  );
};

export default LoginPage; 