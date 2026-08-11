# 🚀 Job3.0 求职系统 - 快速启动指南（SQLite本地版）

**版本**: v1.0.0  
**数据库**: SQLite（本地存储，无需安装）  
**更新时间**: 2026-08-04 14:30  
**开发者**: 林育丞  

---

## 🎯 快速启动（Windows，3分钟）

### 1. 双击启动

`
双击文件：backend\start.bat
`

会自动完成：
- 创建虚拟环境
- 安装依赖
- 初始化数据库
- 启动服务

### 2. 访问

`
后端API：http://localhost:8000/docs
`

---

## 📋 详细启动步骤

### 1. 进入后端目录

`powershell
cd E:\job3.0\backend
`

### 2. 创建虚拟环境

`powershell
python -m venv venv
`

### 3. 激活虚拟环境

`powershell
.\venv\Scripts\activate
`

### 4. 安装依赖

`powershell
pip install -r requirements.txt
`

### 5. 初始化数据库（自动）

`powershell
# 首次启动会自动创建
python -c \"from app.core.database import init_db; init_db()\"
`

### 6. 启动服务

`powershell
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
`

### 7. 配置AI（可选）

`powershell
# 设置API Key
set OPENAI_API_KEY=sk-your-key

# 重新启动
uvicorn app.main:app --reload --port 8000
`

---

## 📂 数据库文件

### SQLite配置

`
文件位置：E:\job3.0\backend\job3.db
文件大小：自动增长
备份方式：复制文件即可
`

### 优势

| 方面 | SQLite | MySQL |
|------|--------|-------|
| 安装 | ❌ 无需安装 | ✅ 需要安装 |
| 部署 | ✅ 复制文件即可 | ❌ 配置复杂 |
| 性能 | ✅ 快速（个人用） | ✅ 强大（企业用） |
| 数据量 | < 10万条 | 无限制 |

---

## 🎯 启动验证

### 1. 检查后端是否启动

打开浏览器访问：

`
http://localhost:8000/health
`

应返回：
`json
{\"status\":\"healthy\"}
`

### 2. 检查API文档

访问：

`
http://localhost:8000/docs
`

可以看到所有API接口。

### 3. 测试简历上传

`ash
curl -X POST \"http://localhost:8000/api/resume/upload\" ^
  -F \"file=@test.pdf\" ^
  -F \"slot=1\"
`

---

## 🔧 常见问题

### Q1: 启动报错"数据库锁定"

**解决**：
`powershell
# 删除锁文件
del job3.db-journal

# 重启服务
uvicorn app.main:app --reload
`

### Q2: 端口被占用

**解决**：
`powershell
# 杀掉占用端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# 或使用其他端口
uvicorn app.main:app --reload --port 8001
`

### Q3: 数据库文件不存在

**解决**：
`powershell
cd backend
python -c \"from app.core.database import init_db; init_db()\"
`

---

## 📦 包含的功能

### ✅ 后端API

| 模块 | 接口数 | 说明 |
|------|--------|------|
| **简历管理** | 6个 | 上传/删除/更新/优化 |
| **投递记录** | 6个 | 添加/更新/删除/重复检测 |
| **打招呼语** | 5个 | 模板CRUD/生成 |
| **JD处理** | 3个 | 解析/OCR/公司安全 |
| **Agent对话** | 2个 | 聊天/建议操作 |
| **AI能力** | 8个 | JD分析/简历匹配/求职建议 |

### ✅ AI能力

| 功能 | 说明 | 需要API Key |
|------|------|-------------|
| 打招呼语生成 | BOSS/猎聘/邮件版 | ✅ |
| JD深度分析 | 提取关键信息+风险 | ✅ |
| 简历智能匹配 | 技能+经验匹配 | ✅ |
| 求职建议 | 策略+公司推荐 | ❌（规则版） |

---

## 🎨 快速测试流程

### 1. 打开API文档

`
http://localhost:8000/docs
`

### 2. 测试打招呼语生成

1. 点击 POST /api/ai/greeting/generate
2. 点击 "Try it out"
3. 输入：
`json
{
  \"resume_info\": {
    \"name\": \"张三\",
    \"experience_summary\": \"3年Python开发经验\",
    \"skills\": [\"Python\", \"Django\", \"Redis\"],
    \"achievements\": [\"优化系统性能30%\"]
  },
  \"jd_content\": \"招聘Python开发工程师，要求熟悉Django，月薪20-35K\"
}
`
4. 点击 "Execute"
5. 查看生成的打招呼语

---

## 🚀 前端启动

`powershell
# 新开一个终端

cd E:\job3.0\frontend
npm install
npm run dev
`

访问：
`
http://localhost:5173
`

---

## 📁 文件清单

`
E:\job3.0\
├── backend/
│   ├── app/
│   │   ├── api/                    # 6个API模块
│   │   ├── agents/                # AI Agent
│   │   ├── models/                # 数据模型
│   │   ├── schemas/               # Pydantic模型
│   │   └── services/              # 业务逻辑
│   │
│   ├── job3.db                   # ⭐ SQLite数据库文件
│   ├── requirements.txt           # Python依赖
│   ├── start.bat                  # ⭐ Windows快速启动
│   ├── start.sh                   # Linux/macOS启动
│   ├── database_guide.md          # 数据库指南
│   └── README.md                  # 使用说明
│
├── frontend/                      # Vue 3前端
│   ├── src/
│   └── package.json
│
├── QUICKSTART.md                  # 本文件
└── README.md                      # 项目总览
`

---

## ⚙️ 配置AI（可选）

### 1. 获取OpenAI API Key

访问：https://platform.openai.com/api-keys

### 2. 配置Key

`powershell
# Windows
set OPENAI_API_KEY=sk-your-key

# Linux/macOS
export OPENAI_API_KEY=sk-your-key
`

### 3. 重启服务

`powershell
uvicorn app.main:app --reload
`

---

## 🎉 启动成功！

`
后端API：http://localhost:8000/docs
前端界面：http://localhost:5173
数据库：E:\job3.0\backend\job3.db
`

---

**有问题？查看详细文档**：
- [数据库指南](backend/database_guide.md)
- [后端错误预警](backend/bad.md)
- [AI Agent指南](backend/app/agents/README.md)
