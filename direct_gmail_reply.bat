@echo off
echo ===================================
echo BRIX Gmail Auto-Reply (Direct)
echo ===================================
echo.

:: Set default number of messages
set NUM_MESSAGES=10
if not "%~1"=="" set NUM_MESSAGES=%~1

echo Will process up to %NUM_MESSAGES% unread messages
echo.

:: Run the Python script
python direct_gmail_reply.py %NUM_MESSAGES%