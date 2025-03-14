import React, { useState, useEffect } from 'react';
import { Layout, Menu, Dropdown, Avatar, Button, Typography, Space } from 'antd';
import { 
  UserOutlined, 
  LogoutOutlined, 
  SettingOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  HomeOutlined,
  FileSearchOutlined,
  TagsOutlined,
  BarChartOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const { Header, Content, Footer, Sider } = Layout;
const { Title, Text } = Typography;

const MainLayout: React.FC = () => {
  const { user, isAuthenticated, logoutUser, fetchCurrentUser } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // 如果已登录但没有用户信息，获取用户信息
  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchCurrentUser();
    }
  }, [isAuthenticated, user, fetchCurrentUser]);

  // 处理登出
  const handleLogout = () => {
    logoutUser();
    navigate('/login');
  };

  // 用户菜单
  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to="/profile">个人资料</Link>
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        <Link to="/change-password">修改密码</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  // 侧边栏菜单项
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/news',
      icon: <FileSearchOutlined />,
      label: <Link to="/news">新闻浏览</Link>,
    },
    {
      key: '/keywords',
      icon: <TagsOutlined />,
      label: <Link to="/keywords">关键词管理</Link>,
    },
    {
      key: '/tasks',
      icon: <ClockCircleOutlined />,
      label: <Link to="/tasks">任务管理</Link>,
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: <Link to="/analytics">数据分析</Link>,
    },
  ];

  // 如果用户是管理员，添加管理员菜单
  if (user?.is_superuser) {
    menuItems.push({
      key: '/admin',
      icon: <SettingOutlined />,
      label: <Link to="/admin">系统管理</Link>,
    });
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        collapsible 
        collapsed={collapsed} 
        onCollapse={setCollapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          padding: '16px'
        }}>
          <Title level={4} style={{ margin: 0, color: '#fff' }}>
            {collapsed ? '锦衣卫' : '锦衣卫系统'}
          </Title>
        </div>
        
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff', 
          display: 'flex', 
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          
          <Space>
            {isAuthenticated ? (
              <Dropdown overlay={userMenu} placement="bottomRight">
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar icon={<UserOutlined />} />
                  <Text>{user?.username || '用户'}</Text>
                </Space>
              </Dropdown>
            ) : (
              <Space>
                <Button type="link">
                  <Link to="/login">登录</Link>
                </Button>
                <Button type="primary">
                  <Link to="/register">注册</Link>
                </Button>
              </Space>
            )}
          </Space>
        </Header>
        
        <Content style={{ margin: '24px 16px', overflow: 'initial' }}>
          <Outlet />
        </Content>
        
        <Footer style={{ textAlign: 'center' }}>
          锦衣卫新闻监控分析系统 ©{new Date().getFullYear()} 版权所有
        </Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 