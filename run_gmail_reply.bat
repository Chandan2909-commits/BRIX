@echo off
setlocal enabledelayedexpansion

echo ===================================
echo BRIX Gmail Auto-Reply
echo ===================================
echo.

:: Set default number of messages
set NUM_MESSAGES=10
if not "%~1"=="" set NUM_MESSAGES=%~1

echo Will process up to %NUM_MESSAGES% unread messages
echo.

:: Create a temporary directory for token storage
set TEMP_DIR=%TEMP%\brix_gmail
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Copy credentials to temp directory
echo Preparing credentials...
copy /Y credentials.json "%TEMP_DIR%\credentials.json" >nul

:: Change to temp directory and run script
echo Running Gmail automation...
cd /d "%TEMP_DIR%"
python "S:\BRIX\brix-tkinter\gmail_auto_reply.py" %NUM_MESSAGES%

:: Copy token back if created
if exist "%TEMP_DIR%\gmail_token.json" (
    copy /Y "%TEMP_DIR%\gmail_token.json" "S:\BRIX\brix-tkinter\gmail_token.json" >nul
)

:: Return to original directory
cd /d "S:\BRIX\brix-tkinter"

echo.
echo Press any key to exit...
pause >nul

endlocal