# 🚨 Job3.0 前后端完整项目 - 错误预警清单

**记录时间**: 2026-08-04 14:16  
**项目**: 智能简历评估与职业规划 Agent 系统  
**版本**: v1.0.0（前后端完整版）  
**开发者**: 林育丞  

---

## 一、项目架构

### 1.1 技术栈

`
前端：
  • Vue 3 + Vite + Pinia
  • Axios HTTP客户端
  • Vue Router 4

后端：
  • Python 3.10+
  • FastAPI + Uvicorn
  • SQLAlchemy ORM
  • MySQL 数据库

可选服务：
  • OpenAI GPT（智能对话）
  • 百度OCR（JD截图识别）
`

### 1.2 项目结构

`
E:\job3.0\
├── frontend/                    # 前端项目（Vue 3）
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/          # 公共组件
│   │   ├── stores/             # Pinia状态
│   │   ├── api/                # API调用
│   │   └── router/             # 路由配置
│   └── package.json
│
├── backend/                    # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic模型
│   │   ├── services/          # 业务逻辑
│   │   ├── core/              # 核心配置
│   │   └── main.py            # 入口文件
│   ├── uploads/               # 文件上传目录
│   ├── requirements.txt
│   └── README.md
│
└── database/                   # 数据库（可选）
`

---

## 二、⚠️ 高优先级预警

### 2.1 数据库连接预警

#### 🔴 预警：MySQL数据库未创建

**风险**：
- 后端启动会报错
- 无法保存数据

**排查步骤**：
`sql
-- 1. 检查MySQL是否运行
SHOW DATABASES;

-- 2. 创建数据库
CREATE DATABASE job3_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. 检查用户权限
GRANT ALL PRIVILEGES ON job3_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
`

**配置文件检查**：
`python
# backend/app/core/config.py
DATABASE_URL = \"mysql+pymysql://root:123456@localhost:3306/job3_db\"
#        ↑            ↑       ↑         ↑         ↑      ↑
#     驱动      用户名   密码    主机      端口    数据库名
`

#### 🔴 预警：pymysql版本兼容性

**风险**：
- SQLAlchemy连接MySQL失败
- 报错：No module named 'pymysql'

**解决**：
`ash
pip install pymysql==1.1.0
pip install cryptography==41.0.7
`

---

### 2.2 前端API调用预警

#### 🔴 预警：跨域请求失败

**风险**：
- 前端调用后端API报CORS错误

**检查后端CORS配置**：
`python
# backend/app/core/config.py
CORS_ORIGINS: list = [
    \"http://localhost:5173\",  # Vite默认端口
    \"http://localhost:3000\",
]
`

**检查前端API基础URL**：
`javascript
// frontend/src/api/index.js
const API_BASE_URL = 'http://localhost:8000/api'
`

#### 🔴 预警：后端未启动

**风险**：
- 前端API调用返回404或网络错误

**启动后端**：
`ash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
`

**验证后端运行**：
`
访问：http://localhost:8000/health
应返回：{\"status\":\"healthy\"}
`

---

### 2.3 文件上传预警

#### 🔴 预警：上传目录不存在

**风险**：
- 简历上传失败
- 报错：[Errno 2] No such file or directory

**解决**：
`ash
# 创建上传目录
mkdir backend/uploads

# 设置权限
chmod 755 backend/uploads
`

**代码中会自动创建**：
`python
# backend/app/core/config.py
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
`

#### 🔴 预警：文件大小超限

**风险**：
- 上传大文件被拒绝
- 默认限制：10MB

**修改限制**：
`python
# backend/app/core/config.py
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
`

#### 🔴 预警：文件类型不支持

**风险**：
- 上传不支持的格式被拒绝

**支持格式**：
`python
ALLOWED_EXTENSIONS: set = {\"pdf\", \"doc\", \"docx\"}
`

---

### 2.4 依赖安装预警

#### 🔴 预警：Python版本不兼容

**风险**：
- 某些依赖安装失败
- 运行时出现语法错误

**要求**：
`
Python 3.10+
`

**检查版本**：
`ash
python --version
`

#### 🔴 预警：依赖安装失败

**常见错误**：

1. **uvloop安装失败**（Windows）：
`
ERROR: No module named 'uvloop'
`
**解决**：Windows不需要uvloop，可以跳过

2. **cryptography编译失败**：
`
Microsoft Visual C++ 14.0 is required
`
**解决**：安装Visual Studio Build Tools，或使用预编译的wheel

3. **sqlalchemy版本冲突**：
`
ImportError: cannot import name 'declarative_base' from 'sqlalchemy.ext.declarative'
`
**解决**：确保安装SQLAlchemy 2.0+：
`ash
pip install sqlalchemy==2.0.23
`

---

## 三、⚠️ 中优先级预警

### 3.1 路由访问预警

#### 🟡 预警：API路由不存在

**检查路由列表**：
`
http://localhost:8000/docs
`
访问此URL查看完整的API文档

**常见路由**：
`
POST   /api/resume/upload         # 上传简历
GET    /api/resume/list           # 简历列表
GET    /api/applications          # 投递记录
POST   /api/greeting/templates    # 创建模板
POST   /api/jd/parse              # 解析JD
POST   /api/agent/chat            # Agent对话
`

#### 🟡 预警：路由参数错误

**常见错误**：

1. **槽位超出范围**：
`
槽位必须是 1-4
`
**检查**：上传简历时slot参数

2. **ID不存在**：
`
记录不存在
`
**检查**：更新/删除时传入的ID

---

### 3.2 数据验证预警

#### 🟡 预警：请求数据格式错误

**常见错误**：

1. **缺少必填字段**：
`python
# resume.py Schema
class ResumeCreate(BaseModel):
    slot: int = Field(..., ge=1, le=4)  # 必填
`
**检查**：确保所有必填字段已传递

2. **字段类型错误**：
`python
# application.py Schema
status: ApplicationStatusEnum  # 枚举类型
`
**检查**：确保status是枚举值

#### 🟡 预警：数据库事务未提交

**风险**：
- 数据保存失败
- 刷新后数据丢失

**检查代码**：
`python
self.db.add(resume)
self.db.commit()  # 必须commit
self.db.refresh(resume)
`

---

### 3.3 服务层预警

#### 🟡 预警：OCR服务未配置

**风险**：
- JD截图识别功能不可用
- 返回错误信息

**配置百度OCR**（可选）：
`ash
# 1. 申请百度OCR账号
# 2. 创建应用，获取App ID、API Key、Secret Key

# 3. 配置环境变量
# .env文件
BAIDU_AIP_APP_ID=xxx
BAIDU_AIP_API_KEY=xxx
BAIDU_AIP_SECRET_KEY=xxx
`

**临时解决方案**：
- 手动复制JD文本
- 不使用截图识别功能

#### 🟡 预警：OpenAI API未配置

**风险**：
- Agent智能对话返回默认回复
- 无法调用GPT

**配置OpenAI**（可选）：
`ash
# .env文件
OPENAI_API_KEY=sk-xxx
`

**临时解决方案**：
- 使用规则匹配回复
- 等待API配置

---

## 四、⚠️ 低优先级预警

### 4.1 性能预警

#### 🟢 预警：大文件解析慢

**风险**：
- PDF/Word解析耗时
- 上传后长时间无响应

**优化建议**：
`python
# 异步处理
async def parse_resume(self, filepath: str):
    # 使用线程池处理
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(None, self._parse_pdf_sync, filepath)
    return content
`

#### 🟢 预警：数据库连接池

**风险**：
- 高并发时连接耗尽

**当前配置**：
`python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接池预检
    pool_recycle=3600,    # 一小时回收
)
`

---

### 4.2 安全预警

#### 🟢 预警：文件上传安全

**风险**：
- 上传恶意文件
- 文件名包含特殊字符

**当前防护**：
`python
# 验证文件扩展名
ext = file.filename.split(\".\")[-1].lower()
if ext not in settings.ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail=\"不支持的文件格式\")

# 重命名文件
filename = f\"resume_{slot}_{uuid.uuid4().hex}.{ext}\"
`

#### 🟢 预警：SQL注入

**风险**：
- 用户输入包含恶意SQL

**当前防护**：
- 使用SQLAlchemy ORM
- 参数化查询
- 无直接SQL拼接

---

### 4.3 日志预警

#### 🟢 预警：日志输出过多

**当前配置**：
`python
# SQLAlchemy配置
echo=settings.DEBUG  # 开发模式打印SQL
`

**生产环境建议**：
`python
echo=False  # 关闭SQL日志
`

---

## 五、常见错误排查清单

### 5.1 后端启动失败

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| ModuleNotFoundError | 依赖未安装 | pip install -r requirements.txt |
| ConnectionRefused | MySQL未运行 | 启动MySQL服务 |
| Access denied | 数据库用户名/密码错误 | 检查config.py |
| Can't connect to MySQL server | 主机/端口错误 | 检查DATABASE_URL |

### 5.2 前端调用失败

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| Network Error | 后端未启动 | 启动后端服务 |
| CORS error | 跨域配置 | 检查CORS_ORIGINS |
| 404 Not Found | 路由错误 | 检查API路径 |
| 500 Internal Server Error | 后端异常 | 查看后端日志 |

### 5.3 文件上传失败

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| File too large | 文件超限 | 减小文件大小 |
| Unsupported format | 文件类型错误 | 使用pdf/doc/docx |
| No space left | 磁盘满 | 清理磁盘空间 |

---

## 六、环境变量配置清单

### 6.1 必须配置

`env
# backend/.env（可选，如果不在代码中硬编码）

# 数据库连接
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/job3_db
`

### 6.2 可选配置

`env
# JWT认证密钥
SECRET_KEY=your-secret-key-here

# OpenAI API（启用AI对话）
OPENAI_API_KEY=sk-xxx

# 百度OCR（启用截图识别）
BAIDU_AIP_APP_ID=xxx
BAIDU_AIP_API_KEY=xxx
BAIDU_AIP_SECRET_KEY=xxx
`

---

## 七、开发自检清单

### 7.1 环境检查

- [ ] Python 3.10+ 已安装
- [ ] MySQL 已安装并运行
- [ ] Node.js 已安装（前端）
- [ ] pip 依赖已安装

### 7.2 数据库检查

- [ ] job3_db 数据库已创建
- [ ] 用户权限已配置
- [ ] 表结构已自动创建（启动时）

### 7.3 前后端联调检查

- [ ] 后端已启动（uvicorn）
- [ ] 前端已启动（npm run dev）
- [ ] API文档可访问（http://localhost:8000/docs）
- [ ] CORS配置正确

### 7.4 功能检查

- [ ] 简历上传成功
- [ ] 简历列表获取成功
- [ ] 投递记录添加成功
- [ ] 打招呼语生成成功
- [ ] JD解析成功
- [ ] Agent对话返回结果

---

## 八、快速启动命令

### 8.1 后端启动

`ash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置MySQL（创建数据库）
mysql -u root -p
CREATE DATABASE job3_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 4. 启动服务
uvicorn app.main:app --reload --port 8000

# 5. 访问API文档
# http://localhost:8000/docs
`

### 8.2 前端启动

`ash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 访问应用
# http://localhost:5173
`

### 8.3 完整流程

`ash
# 终端1：启动后端
cd backend
uvicorn app.main:app --reload --port 8000

# 终端2：启动前端
cd frontend
npm run dev
`

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-08-04 | 前后端完整版，MVP功能 |
| v0.1.0 | 2026-08-04 | 初始前端骨架 |

---

**文档状态**: ✅ 错误预警清单完成  
**下一步**: 启动后端 + 前端，进行功能测试  
**版本**: 1.0.0
