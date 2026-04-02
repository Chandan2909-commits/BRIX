@echo off
echo ===================================
echo BRIX Gmail Auto-Reply (Web Version)
echo ===================================
echo.

:: Set default number of messages
set NUM_MESSAGES=10
if not "%~1"=="" set NUM_MESSAGES=%~1

echo Will process up to %NUM_MESSAGES% unread messages
echo.
echo Starting web server...
echo A browser window will open automatically.
echo.

:: Run the Python script
python gmail_web.py %NUM_MESSAGES%