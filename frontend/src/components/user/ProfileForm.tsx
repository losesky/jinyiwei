import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';
import { updateUserProfile } from '../../api/users';
import { UserUpdate } from '../../types/user';

const ProfileForm: React.FC = () => {
  const { user, fetchCurrentUser } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // 初始化表单数据
  React.useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        full_name: user.full_name || '',
      });
    }
  }, [user, form]);

  // 提交表单
  const onFinish = async (values: UserUpdate) => {
    setLoading(true);
    try {
      await updateUserProfile(values);
      message.success('个人资料更新成功');
      // 重新获取用户信息
      await fetchCurrentUser();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={onFinish}
      style={{ maxWidth: 500, margin: '0 auto' }}
    >
      <Form.Item
        name="username"
        label="用户名"
        rules={[
          { required: true, message: '请输入用户名!' },
          { min: 3, message: '用户名至少3个字符!' },
          { max: 20, message: '用户名最多20个字符!' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线!' },
        ]}
      >
        <Input 
          prefix={<UserOutlined />} 
          placeholder="用户名" 
          disabled  // 用户名不允许修改
        />
      </Form.Item>

      <Form.Item
        name="email"
        label="电子邮箱"
        rules={[
          { required: true, message: '请输入邮箱!' },
          { type: 'email', message: '请输入有效的邮箱地址!' },
        ]}
      >
        <Input 
          prefix={<MailOutlined />} 
          placeholder="邮箱" 
          disabled  // 邮箱不允许修改
        />
      </Form.Item>

      <Form.Item
        name="full_name"
        label="全名"
        rules={[
          { max: 50, message: '全名最多50个字符!' },
        ]}
      >
        <Input 
          prefix={<UserOutlined />} 
          placeholder="全名（可选）" 
        />
      </Form.Item>

      <Form.Item>
        <Button 
          type="primary" 
          htmlType="submit" 
          loading={loading}
          style={{ width: '100%' }}
        >
          更新个人资料
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ProfileForm; 