# Face Recognition Attendance System

A smart attendance management system that uses facial recognition to mark student attendance automatically. Built with Python, OpenCV, and the face_recognition library.

## Features

- **Desktop App** — Webcam-based face recognition with CSV attendance logging
- **Web App** — Full-featured web application with:
  - Student login and face-based attendance marking
  - Admin dashboard to add users and review attendance
  - Calendar view for attendance history
  - SQLite database storage

## Tech Stack

- **Python 3.11+** — Core language
- **OpenCV** — Image processing and webcam capture
- **face_recognition** — Face detection and encoding (dlib)
- **Flask** — Web application framework (web app only)

---

## Prerequisites

- **Python 3.11** (3.12 may work; 3.14 has compatibility issues with some dependencies)
- **Webcam** — For face capture
- **Windows / macOS / Linux** — All supported

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/gauravsahitya62/Face_recognition_attendance_system.git
cd Face_recognition_attendance_system
```

### 2. Create a virtual environment

**Windows (PowerShell or Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
# Core dependencies
pip install dlib-bin opencv-python numpy Pillow Click

# Face recognition (install separately due to dlib)
pip install face_recognition --no-deps
pip install face-recognition-models
```

> **Note for Linux/macOS:** If `dlib-bin` fails, install `dlib` instead (requires CMake and a C++ compiler):
> ```bash
> pip install cmake dlib opencv-python numpy Pillow
> pip install face_recognition
> ```

---

## Option A: Desktop App (Webcam)

### Setup

1. Add face photos to the `Images_Attendance` folder:
   - Formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
   - Use clear, front-facing photos
   - Filename = person's name (e.g., `John.jpg` → "JOHN" in attendance)

### Run

**Windows:**
```bash
venv\Scripts\activate
python AttendanceProject.py
```

**macOS / Linux:**
```bash
source venv/bin/activate
python AttendanceProject.py
```

Or double-click `run.bat` on Windows (if venv already set up).

### Usage

- Webcam opens automatically
- When your face is recognized, attendance is recorded in `Attendance.csv`
- Press **Enter** to exit

---

## Option B: Web App

### Additional dependencies

```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

### Run

**Windows:**
```bash
cd webapp
..\venv\Scripts\python app.py
```

**macOS / Linux:**
```bash
cd webapp
../venv/bin/python app.py
```

Or run `run_webapp.bat` on Windows.

Then open **http://127.0.0.1:5000** in your browser.

### Default credentials

| Role   | User ID | Password   |
|--------|---------|------------|
| Admin  | admin   | admin123   |

### Flow

1. **Admin:** Log in → Add User (with face image) → View students and their attendance
2. **Student:** Log in → Mark Attendance (webcam capture) → View own attendance calendar

---

## Project Structure

```
Face_recognition_attendance_system/
├── AttendanceProject.py    # Desktop app (webcam)
├── main.py                 # Simple face comparison script
├── run.bat                 # Desktop app launcher (Windows)
├── run_webapp.bat          # Web app launcher (Windows)
├── requirements.txt        # Desktop app dependencies
├── Images_Attendance/      # Face images for desktop app
├── Attendance.csv          # Desktop app attendance log
└── webapp/                 # Web application
    ├── app.py              # Flask app
    ├── config.py
    ├── models.py           # User & Attendance models
    ├── face_utils.py       # Face recognition helpers
    ├── requirements.txt
    ├── templates/          # HTML templates
    └── uploads/faces/      # Stored face images (auto-created)
```

---

## Abstract

Manual attendance is time-consuming and prone to proxy attendance. This system automates the process using facial recognition:

1. **Face detection** — OpenCV and dlib locate faces in video frames
2. **Face encoding** — Each face is converted to a 128-dimensional encoding
3. **Matching** — Captured faces are compared against registered faces in the database
4. **Attendance logging** — Recognized students are marked present (CSV or database)

The system works with live webcam feed (desktop) or webcam capture (web app), making it suitable for classrooms and workplaces.

---

## License

MIT
