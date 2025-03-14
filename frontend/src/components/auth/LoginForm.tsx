import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Checkbox, Alert, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const { Title, Text, Paragraph } = Typography;

const LoginForm: React.FC = () => {
  const [form] = Form.useForm();
  const { loginUser, isAuthenticated, loading, error, clearAuthError } = useAuth();
  const navigate = useNavigate();
  const [showError, setShowError] = useState(false);

  // 如果已经登录，重定向到首页
  useEffect(() => {
    console.log('LoginForm: isAuthenticated changed to', isAuthenticated);
    if (isAuthenticated) {
      console.log('LoginForm: Redirecting to home page');
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
    if (errorMsg.includes('login attempts')) {
      return {
        title: '登录尝试次数过多',
        message: '您的账号因多次登录失败已被临时锁定。请稍后再试或联系管理员重置您的账号。'
      };
    } else if (errorMsg.includes('Incorrect') || errorMsg.includes('Invalid')) {
      return {
        title: '用户名或密码错误',
        message: '您输入的用户名或密码不正确。请检查后重试，或点击"忘记密码"重置您的密码。'
      };
    } else if (errorMsg.includes('not active')) {
      return {
        title: '账号未激活',
        message: '您的账号尚未激活。请检查您的邮箱完成激活流程，或联系管理员获取帮助。'
      };
    } else {
      return {
        title: '登录失败',
        message: errorMsg
      };
    }
  };

  // 提交表单
  const onFinish = async (values: { username: string; password: string; remember: boolean }) => {
    console.log('Login form submitted with values:', {
      username: values.username,
      password: '******', // 不记录实际密码
      remember: values.remember
    });
    
    try {
      const result = await loginUser({
        username: values.username,
        password: values.password,
      });
      
      console.log('Login result:', result);
      
      // 如果登录成功但没有自动跳转，手动跳转
      if (result.meta.requestStatus === 'fulfilled') {
        console.log('Login successful, manually navigating to home page');
        // 使用 window.location 强制页面跳转，避免 React Router 的问题
        window.location.href = '/';
      }
    } catch (error) {
      console.error('Login error in form:', error);
    }
    
    // 如果记住我，保存用户名到localStorage
    if (values.remember) {
      localStorage.setItem('rememberedUsername', values.username);
    } else {
      localStorage.removeItem('rememberedUsername');
    }
  };

  // 从localStorage获取保存的用户名
  useEffect(() => {
    const rememberedUsername = localStorage.getItem('rememberedUsername');
    if (rememberedUsername) {
      form.setFieldsValue({ username: rememberedUsername, remember: true });
    }
  }, [form]);

  // 处理错误消息
  const errorInfo = getFriendlyErrorMessage(error);

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: '20px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
        登录
      </Title>
      
      {showError && errorInfo && (
        <Alert
          message={errorInfo.title}
          description={
            <Space direction="vertical">
              <Paragraph>{errorInfo.message}</Paragraph>
              {errorInfo.title.includes('次数过多') && (
                <Paragraph type="warning">
                  <ExclamationCircleOutlined /> 为了保护您的账号安全，系统已临时限制登录。
                </Paragraph>
              )}
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
        name="login"
        initialValues={{ remember: false }}
        onFinish={onFinish}
        size="large"
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名或邮箱!' }]}
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="用户名或邮箱" 
            autoComplete="username"
          />
        </Form.Item>
        
        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码!' }]}
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="密码" 
            autoComplete="current-password"
          />
        </Form.Item>
        
        <Form.Item>
          <Form.Item name="remember" valuePropName="checked" noStyle>
            <Checkbox>记住我</Checkbox>
          </Form.Item>
          
          <Link to="/forgot-password" style={{ float: 'right' }}>
            忘记密码?
          </Link>
        </Form.Item>
        
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            style={{ width: '100%' }}
          >
            登录
          </Button>
        </Form.Item>
        
        <Form.Item style={{ textAlign: 'center' }}>
          <Text>
            还没有账号? <Link to="/register">立即注册</Link>
          </Text>
        </Form.Item>
      </Form>
    </div>
  );
};

export default LoginForm; 