@echo off
title Voice to Anything
py -3.11 "%~dp0voice_to_anything.py"
if %errorlevel% neq 0 (
    echo.
    echo  Something went wrong. Press any key to close.
    pause > nul
)
