# 🚨 Job3.0 数据库配置 - 错误预警清单

**记录时间**: 2026-08-04 14:30  
**数据库**: SQLite（本地存储）  
**版本**: v1.0.0  
**开发者**: 林育丞  

---

## 一、数据库方案

### 1.1 SQLite vs MySQL

| 方面 | SQLite | MySQL |
|------|--------|-------|
| **安装** | 无需安装（内置） | 需要安装服务 |
| **部署** | 单文件 job3.db | 独立数据库服务 |
| **性能** | 适合小数据量 | 适合大数据量 |
| **并发** | 单写多读 | 多写多读 |
| **迁移** | 复制文件即可 | 导出导入SQL |
| **推荐场景** | 个人/小团队 | 企业/多用户 |

### 1.2 当前配置

`python
# backend/app/core/config.py

# 使用SQLite（本地存储）
DATABASE_URL = \"sqlite:///./job3.db\"

# 如果想用MySQL，改为：
# DATABASE_URL = \"mysql+pymysql://root:password@localhost:3306/job3_db\"
`

---

## 二、⚠️ 常见错误

### 2.1 SQLite相关错误

#### 🔴 预警：数据库文件被锁定

**错误信息**：
`
Database is locked
`

**原因**：
- 多个进程同时写入
- 上次操作未正常关闭

**解决**：
`ash
# 删除锁文件
del job3.db-journal
# 或
rm job3.db-journal

# 重启服务
uvicorn app.main:app --reload
`

#### 🔴 预警：数据库文件不存在

**错误信息**：
`
Unable to open database \"job3.db\": file not found
`

**原因**：
- 启动目录不对
- 数据库未初始化

**解决**：
`ash
# 进入backend目录
cd backend

# 初始化数据库
python -c \"from app.core.database import init_db; init_db()\"

# 启动服务
uvicorn app.main:app --reload --port 8000
`

---

### 2.2 MySQL切换问题（可选）

#### 🟡 预警：从SQLite切换到MySQL

**如果之前用SQLite，现在想换MySQL**：

1. **导出数据**：
`ash
# SQLite导出
sqlite3 job3.db .dump > backup.sql
`

2. **创建MySQL数据库**：
`sql
CREATE DATABASE job3_db CHARACTER SET utf8mb4;
`

3. **修改配置**：
`python
# backend/app/core/config.py
DATABASE_URL = \"mysql+pymysql://root:password@localhost:3306/job3_db\"
`

4. **导入数据**：
`ash
mysql -u root -p job3_db < backup.sql
`

---

### 2.3 依赖问题

#### 🟡 预警：缺少SQLAlchemy

**错误信息**：
`
ModuleNotFoundError: No module named 'sqlalchemy'
`

**解决**：
`ash
pip install sqlalchemy==2.0.23
`

#### 🟡 预警：MySQL依赖未安装（如果使用MySQL）

**错误信息**：
`
ModuleNotFoundError: No module named 'pymysql'
`

**解决**：
`ash
pip install pymysql==1.1.0
pip install cryptography==41.0.7
`

---

## 三、⚠️ 数据迁移

### 3.1 备份数据库

`ash
# 复制文件即可
copy job3.db job3_backup.db  # Windows
cp job3.db job3_backup.db    # Linux/macOS
`

### 3.2 恢复数据库

`ash
# 停止服务
# 复制备份文件
copy job3_backup.db job3.db
# 重启服务
`

### 3.3 清空数据

`ash
# 删除数据库文件
del job3.db
# 重启服务（会自动创建）
uvicorn app.main:app --reload
`

---

## 四、⚠️ 路径问题

### 4.1 数据库文件位置

**默认位置**：
`
backend/job3.db  # 相对于backend目录
`

**如果启动失败**，检查：
`ash
# 查看当前目录
cd
# 应该看到 backend 目录

# 查看数据库文件
dir job3.db
`

### 4.2 自定义数据库位置

修改 ackend/app/core/config.py：

`python
# 使用绝对路径
DATABASE_URL = \"sqlite:///C:/Users/LYC/job3.db\"

# 或使用项目根目录
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f\"sqlite:///{os.path.join(BASE_DIR, 'job3.db')}\"
`

---

## 五、⚠️ 性能优化

### 5.1 SQLite性能设置

`python
# backend/app/core/database.py

engine = create_engine(
    \"sqlite:///./job3.db\",
    connect_args={\"check_same_thread\": False},
    echo=False  # 关闭SQL日志提升性能
)
`

### 5.2 索引优化

`python
# backend/app/models/resume.py

class Resume(Base):
    # 为常用查询字段添加索引
    slot = Column(Integer, unique=True, index=True)  # 槽位查询
    created_at = Column(DateTime, index=True)  # 时间排序
`

### 5.3 数据量限制

**SQLite适合**：
- ✅ 个人使用（< 1万条记录）
- ✅ 小团队（< 10个用户）
- ✅ 开发测试环境

**MySQL适合**：
- ⚠️ 大数据量（> 10万条记录）
- ⚠️ 多用户并发（> 10个用户）
- ⚠️ 生产环境

---

## 六、⚠️ 安全提示

### 6.1 数据备份

`ash
# 定期备份
# Windows任务计划程序 或 Linux crontab

# 示例：每天凌晨2点备份
copy job3.db job3_.db
`

### 6.2 文件权限

`ash
# Windows
icacls job3.db /inheritance:r /grant:r Users:R

# Linux/macOS
chmod 600 job3.db
`

---

## 七、快速排查清单

| 问题 | 解决 |
|------|------|
| 数据库锁定 | 删除 job3.db-journal |
| 文件不存在 | 运行 python -c \"from app.core.database import init_db; init_db()\" |
| 依赖错误 | pip install sqlalchemy==2.0.23 |
| 路径错误 | 确认在 ackend 目录启动 |

---

## 八、环境配置清单

### 8.1 必须配置

`ash
# backend/.env（可选）

# SQLite（默认，无需配置）
# DATABASE_URL=sqlite:///./job3.db
`

### 8.2 可选配置（MySQL）

`ash
# 如果使用MySQL
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/job3_db
`

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-08-04 | SQLite本地存储版本 |

---

**文档状态**: ✅ 数据库配置完成  
**数据库**: SQLite (job3.db)  
**版本**: 1.0.0
