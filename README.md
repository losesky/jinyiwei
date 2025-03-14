# 锦衣卫 (Jinyiwei) - 新闻监控分析系统

锦衣卫是一个基于FastAPI和Celery的新闻监控分析系统，能够从多个数据源抓取新闻，进行分析处理，并提供监控和通知功能。

## 主要功能

- 用户认证系统：完整的用户注册、登录和权限管理
- 关键词管理：创建和管理监控关键词
- 新闻爬虫：从多个数据源（百度、谷歌、Bing等）抓取新闻
- 数据处理管道：文本清洗、数据验证、去重和存储优化
- 任务调度系统：基于Celery的分布式任务系统
- 系统监控：健康检查、失败任务重试和告警通知
- 新闻分析：情感分析和摘要生成
- 邮件通知：新闻更新的邮件推送

## 用户认证系统

系统提供了完整的用户认证功能，包括：

- **用户注册**：支持用户名、邮箱和密码注册，可选填写全名
- **用户登录**：使用用户名/邮箱和密码登录，支持JWT令牌认证
- **权限管理**：基于角色的权限控制，区分普通用户和管理员
- **个人资料**：查看和修改个人信息，包括全名等
- **密码管理**：支持修改密码和重置密码功能
- **安全措施**：密码加密存储，登录尝试次数限制，防止暴力破解

### 默认超级管理员账号

系统初始化时会自动创建一个超级管理员账号：

- 用户名：admin
- 密码：Admin123
- 邮箱：admin@example.com

超级管理员拥有系统的所有权限，包括用户管理、系统配置等。

### 用户角色

- **普通用户**：可以管理自己的关键词、查看新闻和分析结果
- **管理员**：拥有所有权限，可以管理所有用户和系统配置

## 技术栈

- 后端：FastAPI, SQLAlchemy, Alembic, Pydantic
- 任务队列：Celery, Redis
- 爬虫：Scrapy
- 数据分析：NLTK, spaCy, scikit-learn, Transformers
- 前端：React, Ant Design, Redux Toolkit
- 数据库：PostgreSQL
- 监控：Prometheus, Sentry

## 安装与设置

### 环境要求

- Python 3.9+
- PostgreSQL
- Redis
- Node.js 16+

### 后端设置

1. 克隆仓库
```bash
git clone https://github.com/losesky/jinyiwei.git
cd jinyiwei
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息
```

5. 运行数据库迁移
```bash
alembic upgrade head
```

6. 初始化数据库（创建超级管理员账号）
```bash
python -m app.db.init_db
```

7. 启动服务
```bash
# 启动API服务
python run.py

# 启动API服务和Celery Worker
python run.py --with-celery

# 启动API服务、Celery Worker和Celery Beat（定时任务）
python run.py --with-celery --with-beat

# 仅启动Celery Worker和Beat（不启动API服务）
python run.py --celery-only

# 自动查找可用端口启动API服务
python run.py --auto-port

# 指定用户运行Celery（可以是用户名或用户ID）
python run.py --with-celery --celery-uid username
```

### 使用管理脚本

项目提供了一个便捷的管理脚本 `manage.sh`，可以简化常见操作：

```bash
# 使脚本可执行
chmod +x manage.sh

# 显示帮助信息
./manage.sh help

# 启动API服务
./manage.sh run

# 启动API服务和Celery Worker
./manage.sh run-celery

# 启动所有服务（API、Celery Worker和Beat）
./manage.sh run-all

# 仅启动Celery服务
./manage.sh celery-only

# 运行数据库迁移
./manage.sh migrate

# 创建新的迁移文件
./manage.sh makemigrations "迁移说明"

# 运行测试
./manage.sh test

# 清理临时文件和缓存
./manage.sh clean
```

管理脚本会自动检查虚拟环境和环境变量文件，简化开发和部署流程。管理脚本默认使用`--auto-port`选项，会自动查找可用端口启动API服务。

### 运行脚本选项

`run.py` 脚本提供了多种命令行选项，方便灵活地启动各种服务：

```
选项:
  -h, --help            显示帮助信息并退出
  --host HOST           指定主机地址 (默认: 0.0.0.0)
  --port PORT           指定端口号 (默认: 8000)
  --reload              启用热重载 (开发模式)
  --workers WORKERS     指定工作进程数 (默认: 1)
  --auto-port           自动查找可用端口 (当指定端口被占用时)
  --with-celery         同时启动Celery Worker
  --with-beat           同时启动Celery Beat调度器
  --celery-only         仅启动Celery服务（不启动API）
  --celery-uid CELERY_UID
                        指定运行Celery的用户名或用户ID
```

### 前端设置

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm start
# 或使用提供的启动脚本
./start.sh
```

4. 访问前端应用
```
http://localhost:3000
```

## 项目结构

```
jinyiwei/
├── app/                    # 后端应用
│   ├── api/                # API路由和端点
│   │   ├── routers/        # 路由模块
│   ├── core/               # 核心配置
│   ├── db/                 # 数据库配置
│   ├── models/             # SQLAlchemy模型
│   ├── schemas/            # Pydantic模型
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   └── workers/            # Celery任务和配置
├── data/                   # 数据文件目录
│   └── celerybeat-schedule # Celery Beat调度文件
├── frontend/               # 前端应用
│   ├── public/             # 静态资源
│   ├── src/                # 源代码
│   │   ├── api/            # API调用
│   │   ├── components/     # React组件
│   │   ├── hooks/          # 自定义Hooks
│   │   ├── layouts/        # 页面布局
│   │   ├── pages/          # 页面组件
│   │   ├── redux/          # Redux状态管理
│   │   ├── routes/         # 路由配置
│   │   ├── types/          # TypeScript类型定义
│   │   └── utils/          # 工具函数
├── logs/                   # 日志文件目录
├── migrations/             # Alembic迁移
├── tests/                  # 测试
├── .env                    # 环境变量
├── .env.example            # 环境变量示例
├── alembic.ini             # Alembic配置
├── requirements.txt        # Python依赖
├── manage.sh               # 项目管理脚本
└── README.md               # 项目文档
```

## API文档

启动后端服务后，可以通过以下URL访问API文档：

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 贡献指南

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE) 