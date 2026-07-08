@echo off
echo ============================================================
echo InsightResume AI - Starting Application
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure your IBM watsonx.ai credentials.
    echo.
    pause
    exit /b 1
)

REM Install/Update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

REM Create uploads directory if it doesn't exist
if not exist "uploads\" (
    mkdir uploads
)

REM Start the application
echo Starting InsightResume AI...
echo.
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
