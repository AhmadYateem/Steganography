@echo off
REM Steganography Suite - Windows Launcher
REM Use this script on Windows systems

echo ======================================================================
echo   Steganography Suite - Apple-Level Professional Interface
echo ======================================================================
echo.

REM Check if Flask-CORS is installed
python -c "import flask_cors" 2>nul
if errorlevel 1 (
    echo Installing Flask-CORS...
    pip install Flask-CORS
    echo.
)

echo Starting Steganography Suite...
echo.
echo Server will run on: http://localhost:5000
echo Open this URL in your browser to see the beautiful interface!
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

REM Start Flask server
python app.py

pause
