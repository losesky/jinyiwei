import React from 'react';
import { Card } from 'antd';
import ChangePasswordForm from '../../components/auth/ChangePasswordForm';

const ChangePasswordPage: React.FC = () => {
  return (
    <div style={{ 
      padding: '20px',
      maxWidth: 800,
      margin: '0 auto'
    }}>
      <Card 
        title="修改密码"
        style={{ 
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}
        bordered={false}
      >
        <ChangePasswordForm />
      </Card>
    </div>
  );
};

export default ChangePasswordPage; 