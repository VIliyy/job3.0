# Job3.0 求职系统 - 后端

## 技术栈

- **框架**: FastAPI + Uvicorn
- **数据库**: MySQL + SQLAlchemy
- **认证**: JWT (可选)
- **文件处理**: 简历解析、JD OCR识别
- **AI服务**: OpenAI GPT (可选)

## 快速开始

### 1. 安装依赖

\\\ash
cd backend
pip install -r requirements.txt
\\\

### 2. 配置数据库

修改 pp/core/config.py:

\\\python
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/job3_db"
\\\

### 3. 启动服务

\\\ash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
\\\

### 4. API文档

启动后访问: http://localhost:8000/docs

## 项目结构

\\\
backend/
├── app/
│   ├── api/           # API路由
│   │   ├── resume.py  # 简历管理
│   │   ├── jd.py      # JD处理
│   │   ├── greeting.py # 打招呼语
│   │   ├── application.py # 投递记录
│   │   └── agent.py   # Agent对话
│   ├── models/        # 数据库模型
│   ├── schemas/       # Pydantic模型
│   ├── services/     # 业务逻辑
│   ├── core/         # 核心配置
│   └── main.py       # 入口
├── uploads/          # 上传文件目录
└── requirements.txt
\\\

## API接口列表

### 简历管理
- POST /api/resume/upload - 上传简历到指定槽位
- GET /api/resume/list - 获取所有简历
- GET /api/resume/{slot} - 获取指定槽位简历
- DELETE /api/resume/{slot} - 删除简历
- POST /api/resume/optimize - 优化简历

### JD处理
- POST /api/jd/parse - 解析JD文本
- POST /api/jd/ocr - OCR识别截图
- GET /api/jd/company-safety - 查询公司安全性

### 打招呼语
- GET /api/greeting/templates - 获取模板列表
- POST /api/greeting/templates - 创建模板
- PUT /api/greeting/templates/{id} - 更新模板
- DELETE /api/greeting/templates/{id} - 删除模板
- POST /api/greeting/generate - 根据JD生成打招呼语

### 投递记录
- GET /api/applications - 获取投递列表
- POST /api/applications - 添加投递
- PUT /api/applications/{id} - 更新投递状态
- DELETE /api/applications/{id} - 删除投递
- GET /api/applications/check-duplicate - 检查重复

### Agent对话
- POST /api/agent/chat - 发送消息

## 开发指南

### 添加新的API

1. 在 pp/schemas/ 添加Pydantic模型
2. 在 pp/services/ 添加业务逻辑
3. 在 pp/api/ 添加路由
4. 在 pp/main.py 注册路由

### 数据库迁移

\\\ash
# 自动创建表
python -m app.core.database init
\\\

## 环境变量

\\\env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/job3_db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-xxx  # 可选
BAIDU_AIP_APP_ID=xxx   # 可选
BAIDU_AIP_API_KEY=xxx  # 可选
BAIDU_AIP_SECRET_KEY=xxx # 可选
\\\

## License

MIT
