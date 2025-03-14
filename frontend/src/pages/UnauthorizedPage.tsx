import React from 'react';
import { Result, Button } from 'antd';
import { Link } from 'react-router-dom';

const UnauthorizedPage: React.FC = () => {
  return (
    <Result
      status="403"
      title="无权限"
      subTitle="抱歉，您没有权限访问此页面。"
      extra={
        <Button type="primary">
          <Link to="/">返回首页</Link>
        </Button>
      }
    />
  );
};

export default UnauthorizedPage; 