@echo off
title Voice to Anything

:: Re-launch as Administrator (required to send keystrokes to other apps)
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title Voice to Anything
py -3.11 "%~dp0voice_to_anything.py"
if %errorlevel% neq 0 (
    echo.
    echo  Something went wrong. Press any key to close.
    pause > nul
)
