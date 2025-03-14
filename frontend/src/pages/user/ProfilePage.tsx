import React, { useEffect, useState } from 'react';
import { Card, Descriptions, Button, Spin, Avatar, Tabs, Typography } from 'antd';
import { UserOutlined, MailOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';
import ChangePasswordForm from '../../components/auth/ChangePasswordForm';
import ProfileForm from '../../components/user/ProfileForm';

const { TabPane } = Tabs;
const { Title } = Typography;

// 格式化日期函数
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) {
    console.log('Date string is undefined or empty');
    return '未知';
  }
  
  console.log('Formatting date string:', dateString);
  
  try {
    // 尝试直接解析日期字符串
    const date = new Date(dateString);
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.log('Invalid date from direct parsing:', dateString);
      
      // 尝试解析ISO格式的日期字符串
      if (typeof dateString === 'string' && dateString.includes('T')) {
        const [datePart, timePart] = dateString.split('T');
        console.log('Trying to parse ISO format:', datePart, timePart);
        
        const newDate = new Date(`${datePart}T${timePart.split('.')[0]}`);
        if (!isNaN(newDate.getTime())) {
          console.log('Successfully parsed ISO format:', newDate);
          return newDate.toLocaleString();
        }
      }
      
      return '未知';
    }
    
    console.log('Successfully parsed date:', date);
    return date.toLocaleString();
  } catch (error) {
    console.error('Error formatting date:', error);
    return '未知';
  }
};

const ProfilePage: React.FC = () => {
  const { user, loading, fetchCurrentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('1');

  useEffect(() => {
    if (!user) {
      fetchCurrentUser();
    }
  }, [user, fetchCurrentUser]);

  // 调试用户数据
  useEffect(() => {
    if (user) {
      console.log('User data:', user);
      console.log('Created at:', user.created_at);
      console.log('Updated at:', user.updated_at);
    }
  }, [user]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!user) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Title level={4}>无法加载用户信息</Title>
          <Button type="primary" onClick={() => fetchCurrentUser()}>
            重试
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: 800, margin: '0 auto' }}>
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Avatar size={64} icon={<UserOutlined />} style={{ marginRight: 16 }} />
            <div>
              <Title level={4} style={{ margin: 0 }}>{user.username}</Title>
              <span>{user.is_superuser ? '管理员' : '普通用户'}</span>
            </div>
          </div>
        }
        style={{ marginBottom: 24, boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' }}
      >
        <Descriptions bordered column={1}>
          <Descriptions.Item label={<><UserOutlined /> 用户名</>}>
            {user.username}
          </Descriptions.Item>
          <Descriptions.Item label={<><MailOutlined /> 电子邮箱</>}>
            {user.email}
          </Descriptions.Item>
          {user.full_name && (
            <Descriptions.Item label={<><UserOutlined /> 全名</>}>
              {user.full_name}
            </Descriptions.Item>
          )}
          <Descriptions.Item label={<><ClockCircleOutlined /> 注册时间</>}>
            {formatDate(user.created_at)}
          </Descriptions.Item>
          <Descriptions.Item label={<><ClockCircleOutlined /> 最后更新</>}>
            {formatDate(user.updated_at)}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card
        style={{ boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' }}
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="个人资料" key="1">
            <ProfileForm />
          </TabPane>
          <TabPane tab="修改密码" key="2">
            <ChangePasswordForm />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default ProfilePage; 