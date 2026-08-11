@echo off
chcp 65001 >nul
color 0A

echo.
echo ============================================================
echo          Job3.0 ???????
echo ============================================================
echo.

cd /d E:\job3.0\backend

echo [1/3] ??Python??...
python --version
if errorlevel 1 (
    echo [ERROR] Python???
    pause
    exit /b 1
)

echo.
echo [2/3] ?????...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [WARN] FastAPI????????...
    pip install -r requirements.txt
)

echo.
echo [3/3] ??????...
echo.
echo ????: http://localhost:8000
echo API??: http://localhost:8000/docs
echo.
echo ? Ctrl+C ????
echo.

uvicorn app.main:app --reload --port 8000

pause
