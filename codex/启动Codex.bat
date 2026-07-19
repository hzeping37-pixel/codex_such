@echo off
chcp 65001 >nul
title Codex

cd /d "%~dp0"

echo ========================================
echo   Codex - AI Code Assistant
echo ========================================
echo.

python --version
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

echo Starting server...
echo Browser will open at http://localhost:8000
echo Press Ctrl+C to stop
echo.

start http://localhost:8000

python main.py

pause
