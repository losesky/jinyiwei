import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Alert, Typography, Result, Space } from 'antd';
import { LockOutlined, InfoCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { confirmPasswordReset } from '../../api/auth';
import { PasswordResetConfirm } from '../../types/user';

const { Title, Text, Paragraph } = Typography;

const ResetPasswordForm: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // 从URL获取token
  const searchParams = new URLSearchParams(location.search);
  const token = searchParams.get('token');
  
  // 如果没有token，重定向到忘记密码页面
  useEffect(() => {
    if (!token) {
      navigate('/forgot-password', { state: { noToken: true } });
    }
  }, [token, navigate]);

  // 获取友好的错误消息
  const getFriendlyErrorMessage = (errorMsg: string | null) => {
    if (!errorMsg) return null;
    
    // 处理常见错误类型
    if (errorMsg.includes('token') && (errorMsg.includes('invalid') || errorMsg.includes('无效'))) {
      return {
        title: '重置链接无效',
        message: '您使用的密码重置链接无效或已被使用。',
        suggestion: '请返回忘记密码页面重新申请一个新的重置链接。',
        action: '重新申请'
      };
    } else if (errorMsg.includes('token') && (errorMsg.includes('expired') || errorMsg.includes('过期'))) {
      return {
        title: '重置链接已过期',
        message: '您使用的密码重置链接已过期。出于安全考虑，重置链接通常在24小时后失效。',
        suggestion: '请返回忘记密码页面重新申请一个新的重置链接。',
        action: '重新申请'
      };
    } else if (errorMsg.includes('password') || errorMsg.includes('密码')) {
      return {
        title: '密码不符合要求',
        message: '您设置的新密码不符合安全要求，请确保密码至少8个字符，并包含大小写字母和数字。',
        suggestion: '一个好的密码例子：Example123',
        action: '修改密码'
      };
    } else {
      return {
        title: '重置失败',
        message: errorMsg,
        suggestion: '请稍后重试，或联系客服获取帮助。',
        action: '重试'
      };
    }
  };

  // 提交表单
  const onFinish = async (values: { password: string; confirmPassword: string }) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      await confirmPasswordReset({
        token,
        new_password: values.password,
      });
      setSuccess(true);
      
      // 3秒后重定向到登录页
      setTimeout(() => {
        navigate('/login', { state: { passwordReset: true } });
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || '重置密码失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理错误消息
  const errorInfo = getFriendlyErrorMessage(error);

  // 如果已经成功重置密码，显示成功信息
  if (success) {
    return (
      <Result
        status="success"
        title="密码重置成功"
        subTitle={
          <Space direction="vertical">
            <Paragraph>您的密码已成功重置，即将跳转到登录页面...</Paragraph>
            <Paragraph type="secondary">
              <InfoCircleOutlined /> 提示：请使用新密码登录您的账号。
            </Paragraph>
          </Space>
        }
        extra={[
          <Button type="primary" key="login">
            <Link to="/login">立即登录</Link>
          </Button>,
        ]}
      />
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: '20px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
        重置密码
      </Title>
      
      {!token && (
        <Alert
          message="无效的重置链接"
          description={
            <Space direction="vertical">
              <Paragraph>您访问的密码重置链接无效或缺少必要的参数。</Paragraph>
              <Paragraph type="secondary">
                <ExclamationCircleOutlined /> 提示：请确保您点击的是完整的重置链接，或重新申请一个新的重置链接。
              </Paragraph>
            </Space>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 20 }}
        />
      )}
      
      {error && errorInfo && (
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
          action={
            errorInfo.title.includes('链接') && (
              <Button size="small" type="primary">
                <Link to="/forgot-password">{errorInfo.action}</Link>
              </Button>
            )
          }
          onClose={() => setError(null)}
        />
      )}
      
      <Form
        form={form}
        name="resetPassword"
        onFinish={onFinish}
        size="large"
      >
        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入新密码!' },
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
            placeholder="新密码" 
            autoComplete="new-password"
          />
        </Form.Item>
        
        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          hasFeedback
          rules={[
            { required: true, message: '请确认新密码!' },
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
            placeholder="确认新密码" 
            autoComplete="new-password"
          />
        </Form.Item>
        
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            style={{ width: '100%' }}
            disabled={!token}
          >
            重置密码
          </Button>
        </Form.Item>
        
        <Form.Item style={{ textAlign: 'center', marginBottom: 0 }}>
          <Space direction="vertical" size="small">
            <Text>
              <Link to="/login">返回登录</Link>
            </Text>
            <Text>
              <Link to="/forgot-password">重新申请重置链接</Link>
            </Text>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ResetPasswordForm; 