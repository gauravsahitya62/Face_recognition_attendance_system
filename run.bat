@echo off
echo Face Recognition Attendance System
echo.
echo Add your face photo to Images_Attendance folder first (e.g., MyName.jpg)
echo.
call venv\Scripts\activate.bat
python AttendanceProject.py
pause
