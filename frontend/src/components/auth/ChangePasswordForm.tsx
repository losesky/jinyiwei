import React, { useState } from 'react';
import { Form, Input, Button, Alert, Typography, Result, Space } from 'antd';
import { LockOutlined, InfoCircleOutlined, SafetyOutlined } from '@ant-design/icons';
import { changePassword } from '../../api/auth';
import { PasswordChange } from '../../types/user';

const { Title, Text, Paragraph } = Typography;

const ChangePasswordForm: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // 获取友好的错误消息
  const getFriendlyErrorMessage = (errorMsg: string | null) => {
    if (!errorMsg) return null;
    
    // 处理常见错误类型
    if (errorMsg.includes('current password') || errorMsg.includes('当前密码') || errorMsg.includes('incorrect')) {
      return {
        title: '当前密码错误',
        message: '您输入的当前密码不正确，请重新输入。',
        suggestion: '如果您忘记了当前密码，可以使用"忘记密码"功能重置密码。'
      };
    } else if (errorMsg.includes('new password') || errorMsg.includes('新密码')) {
      return {
        title: '新密码不符合要求',
        message: '您设置的新密码不符合安全要求，请确保密码至少8个字符，并包含大小写字母和数字。',
        suggestion: '一个好的密码例子：Example123'
      };
    } else if (errorMsg.includes('same as') || errorMsg.includes('相同')) {
      return {
        title: '新密码不能与当前密码相同',
        message: '为了安全起见，新密码不能与当前密码相同。',
        suggestion: '请设置一个与当前密码不同的新密码。'
      };
    } else if (errorMsg.includes('token') || errorMsg.includes('认证')) {
      return {
        title: '会话已过期',
        message: '您的登录会话已过期，请重新登录后再修改密码。',
        suggestion: '点击右上角的退出按钮，然后重新登录。'
      };
    } else {
      return {
        title: '修改失败',
        message: errorMsg,
        suggestion: '请稍后重试，或联系客服获取帮助。'
      };
    }
  };

  // 提交表单
  const onFinish = async (values: { 
    currentPassword: string; 
    newPassword: string; 
    confirmPassword: string 
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      await changePassword({
        current_password: values.currentPassword,
        new_password: values.newPassword,
      });
      setSuccess(true);
      form.resetFields();
    } catch (err: any) {
      setError(err.response?.data?.detail || '修改密码失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理错误消息
  const errorInfo = getFriendlyErrorMessage(error);

  // 如果已经成功修改密码，显示成功信息
  if (success) {
    return (
      <Result
        status="success"
        title="密码修改成功"
        subTitle={
          <Space direction="vertical">
            <Paragraph>您的密码已成功修改，下次登录请使用新密码。</Paragraph>
            <Paragraph type="secondary">
              <InfoCircleOutlined /> 提示：为了安全起见，您可能需要在其他设备上重新登录。
            </Paragraph>
          </Space>
        }
        extra={[
          <Button 
            type="primary" 
            key="continue" 
            onClick={() => setSuccess(false)}
          >
            继续
          </Button>,
        ]}
      />
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: '20px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
        修改密码
      </Title>
      
      <Alert
        message="安全提示"
        description="为了保护您的账户安全，请定期修改密码，并避免使用与其他网站相同的密码。"
        type="info"
        showIcon
        icon={<SafetyOutlined />}
        style={{ marginBottom: 20 }}
      />
      
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
        name="changePassword"
        onFinish={onFinish}
        size="large"
      >
        <Form.Item
          name="currentPassword"
          rules={[
            { required: true, message: '请输入当前密码!' },
          ]}
          tooltip="请输入您当前的登录密码"
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="当前密码" 
            autoComplete="current-password"
          />
        </Form.Item>
        
        <Form.Item
          name="newPassword"
          rules={[
            { required: true, message: '请输入新密码!' },
            { min: 8, message: '密码至少8个字符!' },
            { 
              pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, 
              message: '密码必须包含大小写字母和数字!' 
            },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('currentPassword') !== value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('新密码不能与当前密码相同!'));
              },
            }),
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
          dependencies={['newPassword']}
          hasFeedback
          rules={[
            { required: true, message: '请确认新密码!' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('newPassword') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致!'));
              },
            }),
          ]}
          tooltip="请再次输入新密码以确认"
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
          >
            修改密码
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ChangePasswordForm; 