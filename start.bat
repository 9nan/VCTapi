@echo off

echo Installing required packages...
pip install -r requirements.txt

echo Starting VLR.GG API server...
echo Server will be available at: http://127.0.0.1:3001
echo.

uvicorn main:app --reload --host 127.0.0.1 --port 3001

pause