# 锦衣卫前端

锦衣卫新闻监控分析系统的前端部分，基于React和Ant Design构建。

## 功能特性

- 用户认证：登录、注册和权限管理
- 关键词管理：创建、查看、更新和删除监控关键词
- 新闻浏览：查看和搜索新闻，支持多种筛选条件
- 任务管理：启动和监控爬虫任务
- 数据可视化：新闻情感分析和趋势图表
- 响应式设计：适配桌面和移动设备

## 技术栈

- React 18
- Ant Design 5
- React Router 6
- Redux Toolkit
- Axios
- Echarts
- TypeScript

## 开发环境设置

### 前提条件

- Node.js 16+
- npm 8+

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm start
```

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── public/                # 静态资源
├── src/                   # 源代码
│   ├── api/               # API请求
│   ├── assets/            # 静态资源
│   ├── components/        # 通用组件
│   ├── hooks/             # 自定义钩子
│   ├── layouts/           # 布局组件
│   ├── pages/             # 页面组件
│   ├── redux/             # Redux状态管理
│   ├── routes/            # 路由配置
│   ├── services/          # 服务
│   ├── types/             # TypeScript类型定义
│   ├── utils/             # 工具函数
│   ├── App.tsx            # 应用入口
│   ├── index.tsx          # 渲染入口
│   └── setupTests.ts      # 测试配置
├── .env                   # 环境变量
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript配置
└── README.md              # 项目文档
```

## 开发规范

- 使用TypeScript编写所有代码
- 使用函数组件和React Hooks
- 使用ESLint和Prettier保持代码风格一致
- 遵循组件化开发原则
- 使用Redux Toolkit管理全局状态

## 部署

### 构建Docker镜像

```bash
docker build -t jinyiwei-frontend .
```

### 运行Docker容器

```bash
docker run -p 80:80 jinyiwei-frontend
``` 