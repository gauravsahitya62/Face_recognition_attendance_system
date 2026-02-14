@echo off
echo Face Recognition Attendance - Web App
echo.
cd /d "%~dp0"
if not exist "venv\Scripts\activate.bat" (
    echo Run: py -3.11 -m venv venv
    echo Then: venv\Scripts\activate
    echo       pip install -r webapp\requirements.txt
    echo       pip install face-recognition-models --no-deps
    echo       pip install face-recognition-models
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
pip install flask flask-sqlalchemy flask-login werkzeug 2>nul
cd webapp
python app.py
pause
