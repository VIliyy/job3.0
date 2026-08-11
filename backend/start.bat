@echo off
chcp 65001 > nul
title Job3.0 后端服务

echo ========================================
echo   Job3.0 求职系统 - 后端启动
echo ========================================
echo.

cd /d %~dp0

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist venv (
    echo [步骤1] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [步骤2] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [步骤3] 安装依赖...
pip install -r requirements.txt --quiet

REM 检查数据库
if not exist job3.db (
    echo [步骤4] 初始化SQLite数据库...
    python -c \"from app.core.database import init_db; init_db()\"
)

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 数据库: SQLite (本地存储)
echo 数据库文件: job3.db
echo 上传目录: ..\\uploads
echo.
echo API文档: http://localhost:8000/docs
echo.

REM 启动服务
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

pause
