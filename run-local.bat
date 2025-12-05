@echo off
REM Run both backend and frontend from root directory (Windows)

echo 🚀 Starting Insightor...
echo.

REM Start Backend
echo 📦 Starting Backend on port 8000...
cd backend
call venv\Scripts\activate.bat
start "Backend" cmd /k python run.py

REM Wait a moment for backend to start
timeout /t 2

REM Start Frontend
echo 📦 Starting Frontend on port 3000...
cd ..\frontend
start "Frontend" cmd /k npm run dev

echo.
echo ✅ Both services started!
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the services
echo.

REM Keep main window open
pause
