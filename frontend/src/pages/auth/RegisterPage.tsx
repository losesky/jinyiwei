import React from 'react';
import { Card } from 'antd';
import RegisterForm from '../../components/auth/RegisterForm';

const RegisterPage: React.FC = () => {
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
        <RegisterForm />
      </Card>
    </div>
  );
};

export default RegisterPage; 