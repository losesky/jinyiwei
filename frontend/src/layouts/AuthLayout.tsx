import React from 'react';
import { Layout, Typography } from 'antd';
import { Outlet } from 'react-router-dom';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const AuthLayout: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#fff', 
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px'
      }}>
        <Title level={3} style={{ margin: 0 }}>
          锦衣卫新闻监控分析系统
        </Title>
      </Header>
      
      <Content>
        <Outlet />
      </Content>
      
      <Footer style={{ textAlign: 'center' }}>
        锦衣卫新闻监控分析系统 ©{new Date().getFullYear()} 版权所有
      </Footer>
    </Layout>
  );
};

export default AuthLayout; 