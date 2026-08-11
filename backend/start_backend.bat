@echo off
cd /d E:\job3.0\backend
echo Starting backend server...
uvicorn app.main:app --reload --port 8000
pause
