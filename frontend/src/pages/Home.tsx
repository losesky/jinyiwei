import React from 'react';
import { Card, Typography, Alert } from 'antd';
import { useAuth } from '../hooks/useAuth';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const { user, isAuthenticated, token } = useAuth();

  return (
    <Card>
      <Typography>
        <Title level={2}>欢迎使用锦衣卫新闻监控分析系统</Title>
        
        {/* 调试信息 */}
        <Alert
          message="认证状态"
          description={
            <div>
              <p><strong>是否已认证:</strong> {isAuthenticated ? '是' : '否'}</p>
              <p><strong>Token:</strong> {token ? `${token.substring(0, 20)}...` : '无'}</p>
              <p><strong>用户信息:</strong> {user ? `${user.username} (${user.email})` : '无'}</p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 20 }}
        />
        
        <Paragraph>
          这是一个基于React和Ant Design构建的新闻监控分析系统前端界面。
          系统提供以下主要功能：
        </Paragraph>
        <ul>
          <li>用户认证：登录、注册和权限管理</li>
          <li>关键词管理：创建、查看、更新和删除监控关键词</li>
          <li>新闻浏览：查看和搜索新闻，支持多种筛选条件</li>
          <li>任务管理：启动和监控爬虫任务</li>
          <li>数据可视化：新闻情感分析和趋势图表</li>
        </ul>
      </Typography>
    </Card>
  );
};

export default Home; 