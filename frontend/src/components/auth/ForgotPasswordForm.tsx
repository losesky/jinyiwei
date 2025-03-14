import React, { useState } from 'react';
import { Form, Input, Button, Alert, Typography, Result, Space } from 'antd';
import { MailOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { requestPasswordReset } from '../../api/auth';
import { PasswordResetRequest } from '../../types/user';

const { Title, Text, Paragraph } = Typography;

const ForgotPasswordForm: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [email, setEmail] = useState('');

  // 获取友好的错误消息
  const getFriendlyErrorMessage = (errorMsg: string | null) => {
    if (!errorMsg) return null;
    
    // 处理常见错误类型
    if (errorMsg.includes('not found') || errorMsg.includes('不存在')) {
      return {
        title: '邮箱未注册',
        message: '该邮箱地址未在系统中注册。请检查您输入的邮箱是否正确，或使用其他邮箱尝试。',
        suggestion: '如果您确定这是您的注册邮箱，请尝试使用您可能使用的其他邮箱，或直接注册一个新账号。'
      };
    } else if (errorMsg.includes('too many requests') || errorMsg.includes('请求过于频繁')) {
      return {
        title: '请求过于频繁',
        message: '您最近已经请求过密码重置。请稍后再试，或检查您的邮箱是否已收到之前发送的重置邮件。',
        suggestion: '请检查您的垃圾邮件文件夹，有时重置邮件可能会被误归类为垃圾邮件。'
      };
    } else {
      return {
        title: '发送失败',
        message: errorMsg,
        suggestion: '请稍后重试，或联系客服获取帮助。'
      };
    }
  };

  // 提交表单
  const onFinish = async (values: PasswordResetRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      await requestPasswordReset(values);
      setSuccess(true);
      setEmail(values.email);
    } catch (err: any) {
      setError(err.response?.data?.detail || '发送重置邮件失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理错误消息
  const errorInfo = getFriendlyErrorMessage(error);

  // 如果已经成功发送重置邮件，显示成功信息
  if (success) {
    return (
      <Result
        status="success"
        title="重置密码邮件已发送"
        subTitle={
          <Space direction="vertical">
            <Paragraph>我们已向 {email} 发送了一封包含密码重置链接的邮件。</Paragraph>
            <Paragraph>请检查您的邮箱，并按照邮件中的指示重置密码。</Paragraph>
            <Paragraph type="secondary">
              <InfoCircleOutlined /> 提示：如果您没有收到邮件，请检查垃圾邮件文件夹，或在几分钟后重试。
            </Paragraph>
          </Space>
        }
        extra={[
          <Button type="primary" key="login">
            <Link to="/login">返回登录</Link>
          </Button>,
          <Button key="retry" onClick={() => setSuccess(false)}>
            重新发送
          </Button>
        ]}
      />
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: '20px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
        忘记密码
      </Title>
      
      <Text style={{ display: 'block', marginBottom: 20 }}>
        请输入您的注册邮箱，我们将向您发送一封包含密码重置链接的邮件。
      </Text>
      
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
          onClose={() => setError(null)}
        />
      )}
      
      <Form
        form={form}
        name="forgotPassword"
        onFinish={onFinish}
        size="large"
      >
        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱!' },
            { type: 'email', message: '请输入有效的邮箱地址!' },
          ]}
          tooltip="请输入您注册时使用的邮箱地址"
        >
          <Input 
            prefix={<MailOutlined />} 
            placeholder="邮箱" 
            autoComplete="email"
          />
        </Form.Item>
        
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            style={{ width: '100%' }}
          >
            发送重置链接
          </Button>
        </Form.Item>
        
        <Form.Item style={{ textAlign: 'center', marginBottom: 0 }}>
          <Space direction="vertical" size="small">
            <Text>
              <Link to="/login">返回登录</Link>
            </Text>
            <Text type="secondary">
              还没有账号? <Link to="/register">立即注册</Link>
            </Text>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ForgotPasswordForm; 