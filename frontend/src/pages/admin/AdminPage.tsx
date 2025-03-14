import React, { useState, useEffect } from 'react';
import { Card, Typography, Table, Button, Space, Tag, message, Modal } from 'antd';
import { DeleteOutlined, EditOutlined, LockOutlined } from '@ant-design/icons';
import { User } from '../../types/user';

const { Title } = Typography;

const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  // 模拟获取用户列表
  useEffect(() => {
    setLoading(true);
    // 这里应该调用API获取用户列表，但目前后端没有提供该接口
    // 所以我们模拟一些数据
    setTimeout(() => {
      setUsers([
        {
          id: '1',
          username: 'admin',
          email: 'admin@example.com',
          full_name: '管理员',
          is_active: true,
          is_superuser: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: '2',
          username: 'user1',
          email: 'user1@example.com',
          full_name: '用户1',
          is_active: true,
          is_superuser: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: '3',
          username: 'user2',
          email: 'user2@example.com',
          full_name: undefined,
          is_active: false,
          is_superuser: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  // 删除用户
  const handleDelete = (userId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此用户吗？此操作不可逆。',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        // 这里应该调用API删除用户
        message.success('用户删除成功（模拟）');
        setUsers(users.filter(user => user.id !== userId));
      },
    });
  };

  // 编辑用户
  const handleEdit = (userId: string) => {
    message.info('编辑用户功能正在开发中...');
  };

  // 重置密码
  const handleResetPassword = (userId: string) => {
    Modal.confirm({
      title: '确认重置密码',
      content: '确定要重置此用户的密码吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        // 这里应该调用API重置用户密码
        message.success('密码重置成功（模拟）');
      },
    });
  };

  // 表格列定义
  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '全名',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (text: string | undefined) => text || '-',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '激活' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '角色',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      render: (isSuperuser: boolean) => (
        <Tag color={isSuperuser ? 'blue' : 'default'}>
          {isSuperuser ? '管理员' : '普通用户'}
        </Tag>
      ),
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: User) => (
        <Space size="middle">
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record.id)}
          />
          <Button 
            type="text" 
            icon={<LockOutlined />} 
            onClick={() => handleResetPassword(record.id)}
          />
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record.id)}
            disabled={record.is_superuser}  // 禁止删除超级管理员
          />
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={4} style={{ margin: 0 }}>用户管理</Title>
            <Button type="primary">
              添加用户
            </Button>
          </div>
        }
        style={{ boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' }}
      >
        <Table 
          columns={columns} 
          dataSource={users} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default AdminPage; 