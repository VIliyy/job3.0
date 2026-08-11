# Job3.0 后端 - 快速启动脚本

# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
# .\venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python -c \"from app.core.database import init_db; init_db()\"

# 5. 启动服务
uvicorn app.main:app --reload --port 8000
