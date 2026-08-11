# Job3.0 - 智能简历优化平台

基于多Agent协作系统的智能简历优化平台，支持简历管理、JD分析、投递记录等功能。

## 功能特性

- 📄 **简历管理** - 多版本简历管理，快速切换
- 🔍 **JD分析** - 智能解析职位描述，提取关键信息
- 🤖 **AI优化** - 多Agent协作，自动优化简历
- 📊 **匹配分析** - 简历与JD智能匹配度分析
- 📋 **投递管理** - 记录求职进度，不错过机会
- 💬 **智能助手** - AI对话，随时解答求职问题

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Pinia (状态管理)
- Axios (HTTP客户端)

### 后端
- FastAPI
- SQLAlchemy
- LangGraph (多Agent框架)
- DeepSeek / OpenAI API

### 部署
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/job3.0.git
cd job3.0
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填写 API Key
```

### 3. 启动开发服务

**后端:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Docker部署 (生产环境)
```bash
docker-compose up -d
```

## 项目结构

```
job3.0/
├── frontend/           # 前端项目
│   ├── src/
│   │   ├── components/  # Vue组件
│   │   ├── views/       # 页面视图
│   │   ├── stores/      # Pinia状态
│   │   ├── api/         # API封装
│   │   └── types/       # TypeScript类型
│   └── ...
│
├── backend/            # 后端项目
│   ├── app/
│   │   ├── api/        # API路由
│   │   ├── core/       # 核心配置
│   │   ├── models/     # 数据库模型
│   │   ├── schemas/    # Pydantic模型
│   │   ├── services/   # 业务逻辑
│   │   └── agents/     # AI Agent
│   └── tests/          # 测试文件
│
├── docker-compose.yml  # Docker编排
├── nginx.conf          # Nginx配置
├── Dockerfile          # 后端镜像
└── .env.example        # 环境变量示例
```

## 开发指南

### 前端开发
```bash
# 类型检查
npm run type-check

# 代码检查
npm run lint

# 代码格式化
npm run format

# 运行测试
npm run test

# 构建生产版本
npm run build
```

### 后端开发
```bash
# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=app --cov-report=html

# API文档
# 访问 http://localhost:8000/docs
```

## API文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境变量说明

| 变量名 | 说明 | 必填 |
|--------|------|------|
| DEEPSEEK_API_KEY | DeepSeek API Key | 是 |
| OPENAI_API_KEY | OpenAI API Key | 否 |
| DATABASE_URL | 数据库连接URL | 否 |
| SECRET_KEY | JWT密钥 | 生产必填 |

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '\''Add some amazing feature'\'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## License

MIT License
