@echo off
title Voice to Anything - Installer
echo.
echo  ================================================
echo          Voice to Anything - Installer
echo  ================================================
echo.

:: Check Python
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python 3.11 not found. Installing...
    winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
) else (
    echo  [OK] Python 3.11 found.
)

:: Check ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] FFmpeg not found. Installing...
    winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
) else (
    echo  [OK] FFmpeg found.
)

:: Install Python packages
echo.
echo  Installing Python packages...
py -3.11 -m pip install --upgrade pip >nul 2>&1
py -3.11 -m pip install pyaudio whisper pyperclip keyboard pyautogui numpy openai-whisper

echo.
echo  Creating desktop shortcut...

:: Get script directory
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

:: Create shortcut via PowerShell
powershell -ExecutionPolicy Bypass -Command ^
  "$s = New-Object -ComObject WScript.Shell; ^
   $d = [Environment]::GetFolderPath('Desktop'); ^
   $sc = $s.CreateShortcut($d + '\Voice to Anything.lnk'); ^
   $sc.TargetPath = '%SCRIPT_DIR%\launch.bat'; ^
   $sc.WorkingDirectory = '%SCRIPT_DIR%'; ^
   $sc.IconLocation = 'C:\Windows\System32\Speech\SpeechUX\sapi.cpl,0'; ^
   $sc.Save()"

echo.
echo  ================================================
echo   Done! Shortcut created on your Desktop.
echo   Double-click "Voice to Anything" to start.
echo  ================================================
echo.
pause
