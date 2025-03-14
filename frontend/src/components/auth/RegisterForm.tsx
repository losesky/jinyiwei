import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Alert, Typography, Checkbox, Space } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, UserAddOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const { Title, Text, Paragraph } = Typography;

const RegisterForm: React.FC = () => {
  const { registerUser, isAuthenticated, loading, error, clearAuthError } = useAuth();
  const navigate = useNavigate();
  const [showError, setShowError] = useState(false);
  const [form] = Form.useForm();

  // 如果已经登录，重定向到首页
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  // 处理错误显示
  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => {
        setShowError(false);
        clearAuthError();
      }, 10000); // 增加显示时间到10秒，让用户有足够时间阅读
      return () => clearTimeout(timer);
    }
  }, [error, clearAuthError]);

  // 获取友好的错误消息
  const getFriendlyErrorMessage = (errorMsg: string | null) => {
    if (!errorMsg) return null;
    
    // 处理常见错误类型
    if (errorMsg.includes('username already exists') || errorMsg.includes('Username already exists')) {
      return {
        title: '用户名已存在',
        message: '该用户名已被注册，请尝试使用其他用户名。',
        suggestion: '您可以尝试添加数字或其他字符来创建一个独特的用户名。'
      };
    } else if (errorMsg.includes('email already exists') || errorMsg.includes('Email already exists')) {
      return {
        title: '邮箱已注册',
        message: '该邮箱地址已被注册，请使用其他邮箱或尝试找回密码。',
        suggestion: '如果这是您的邮箱，您可以尝试直接登录或使用"忘记密码"功能。'
      };
    } else if (errorMsg.includes('password') || errorMsg.includes('Password')) {
      return {
        title: '密码不符合要求',
        message: '您设置的密码不符合安全要求，请确保密码至少8个字符，并包含大小写字母和数字。',
        suggestion: '一个好的密码例子：Example123'
      };
    } else {
      return {
        title: '注册失败',
        message: errorMsg,
        suggestion: '请检查您的输入并重试，或联系客服获取帮助。'
      };
    }
  };

  // 提交表单
  const onFinish = async (values: { 
    username: string; 
    email: string; 
    password: string; 
    confirmPassword: string;
    fullName?: string;
    agreement: boolean;
  }) => {
    // 如果没有同意协议，不提交
    if (!values.agreement) {
      return;
    }
    
    console.log('Register form submitted with values:', {
      username: values.username,
      email: values.email,
      password: '******', // 不记录实际密码
      confirmPassword: '******', // 不记录实际密码
      fullName: values.fullName || '',
      agreement: values.agreement
    });
    
    try {
      // 确保fullName不是空字符串
      const userData = {
        username: values.username,
        email: values.email,
        password: values.password,
        full_name: values.fullName?.trim() || undefined,  // 如果为空字符串，则设为undefined
      };
      
      console.log('Processed registration data:', {
        ...userData,
        password: '******' // 不记录实际密码
      });
      
      await registerUser(userData);
      
      // 注册成功后跳转到登录页
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      console.error('Registration error in form:', err);
      // 错误处理在Redux中
    }
  };

  // 处理错误消息
  const errorInfo = getFriendlyErrorMessage(error);

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: '20px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
        注册账号
      </Title>
      
      {showError && errorInfo && (
        <Alert
          message={errorInfo.title}
          description={
            <Space direction="vertical">
              <Paragraph>{errorInfo.message}</Paragraph>
              <Paragraph type="secondary">
                <InfoCircleOutlined /> 提示：{errorInfo.suggestion}
              </Paragraph>
            </Space>
          }
          type="error"
          showIcon
          closable
          style={{ marginBottom: 20 }}
          onClose={() => {
            setShowError(false);
            clearAuthError();
          }}
        />
      )}
      
      <Form
        form={form}
        name="register"
        onFinish={onFinish}
        size="large"
        scrollToFirstError
      >
        <Form.Item
          name="username"
          rules={[
            { required: true, message: '请输入用户名!' },
            { min: 3, message: '用户名至少3个字符!' },
            { max: 20, message: '用户名最多20个字符!' },
            { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线!' },
          ]}
          tooltip="用户名将用于登录，只能包含字母、数字和下划线，长度3-20个字符"
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="用户名" 
            autoComplete="username"
          />
        </Form.Item>
        
        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱!' },
            { type: 'email', message: '请输入有效的邮箱地址!' },
          ]}
          tooltip="邮箱将用于找回密码和接收通知"
        >
          <Input 
            prefix={<MailOutlined />} 
            placeholder="邮箱" 
            autoComplete="email"
          />
        </Form.Item>
        
        <Form.Item
          name="fullName"
          rules={[
            { max: 50, message: '全名最多50个字符!' },
          ]}
          tooltip="全名是可选的，将用于个性化您的体验"
        >
          <Input 
            prefix={<UserAddOutlined />} 
            placeholder="全名（可选）" 
            autoComplete="name"
          />
        </Form.Item>
        
        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入密码!' },
            { min: 8, message: '密码至少8个字符!' },
            { 
              pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, 
              message: '密码必须包含大小写字母和数字!' 
            },
          ]}
          tooltip="密码必须至少8个字符，并包含大小写字母和数字"
          hasFeedback
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="密码" 
            autoComplete="new-password"
          />
        </Form.Item>
        
        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          hasFeedback
          rules={[
            { required: true, message: '请确认密码!' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致!'));
              },
            }),
          ]}
          tooltip="请再次输入密码以确认"
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="确认密码" 
            autoComplete="new-password"
          />
        </Form.Item>
        
        <Form.Item
          name="agreement"
          valuePropName="checked"
          rules={[
            {
              validator: (_, value) =>
                value ? Promise.resolve() : Promise.reject(new Error('请阅读并同意用户协议')),
            },
          ]}
        >
          <Checkbox>
            我已阅读并同意 <Link to="/terms">用户协议</Link> 和 <Link to="/privacy">隐私政策</Link>
          </Checkbox>
        </Form.Item>
        
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            style={{ width: '100%' }}
          >
            注册
          </Button>
        </Form.Item>
        
        <Form.Item style={{ textAlign: 'center' }}>
          <Text>
            已有账号? <Link to="/login">立即登录</Link>
          </Text>
        </Form.Item>
      </Form>
    </div>
  );
};

export default RegisterForm; 