@echo off
REM Setup script for Insightor Project (Windows)
REM Run this script to set up the entire project

echo 🚀 Insightor Setup Script
echo ==========================
echo.

REM Backend Setup
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

REM Copy .env.example to .env
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env with your API keys:
    echo    GOOGLE_API_KEY=your_key_here
    echo    TAVILY_API_KEY=your_key_here
)

echo ✅ Backend setup complete!
echo.

REM Frontend Setup
echo 📦 Setting up Frontend...
cd ..\frontend

REM Install dependencies
echo Installing frontend dependencies...
call npm install

echo ✅ Frontend setup complete!
echo.

REM Final instructions
echo 🎉 Setup Complete!
echo ====================
echo.
echo To run the application:
echo.
echo 1. In a terminal, start the backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python run.py
echo.
echo 2. In another terminal, start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open http://localhost:3000 in your browser
echo.
echo API Documentation: http://localhost:8000/docs
echo.
