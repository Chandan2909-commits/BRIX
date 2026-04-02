@echo off
echo ===================================
echo BRIX Gmail Auto-Reply (PowerShell)
echo ===================================
echo.

:: Set default number of messages
set NUM_MESSAGES=10
if not "%~1"=="" set NUM_MESSAGES=%~1

:: Run PowerShell script with elevated privileges
powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"S:\BRIX\brix-tkinter\GmailAutoReply.ps1\" -MessageCount %NUM_MESSAGES%' -Verb RunAs"