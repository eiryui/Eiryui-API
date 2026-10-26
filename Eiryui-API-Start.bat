@echo off
setlocal EnableExtensions
title Eiryui API - Server Launcher

set "SCRIPTDIR=%~dp0"
cd /d "%SCRIPTDIR%"

echo.
echo ============================================================
echo   Eiryui API - Server Launcher
echo ============================================================
echo.

echo Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python was not found in PATH.
    echo         Install Python from https://python.org/downloads
    echo         and enable "Add Python to PATH".
    goto :fatal
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo        %%i found.

if not exist "requirements.txt" (
    echo.
    echo [ERROR] requirements.txt was not found.
    goto :fatal
)

if not exist "api.py" (
    echo.
    echo [ERROR] api.py was not found.
    goto :fatal
)

echo.
echo Installing or updating dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed.
    goto :fatal
)

echo.
echo Starting Eiryui API at http://127.0.0.1:4000
echo Press Ctrl+C to stop the server.
echo.
python -m uvicorn api:app --reload --host 0.0.0.0 --port 4000
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Eiryui API stopped cleanly.
) else (
    echo Eiryui API exited with code %EXIT_CODE%.
)
echo.
pause
exit /b %EXIT_CODE%

:fatal
echo.
echo [FATAL] Eiryui API could not be started.
echo.
pause
exit /b 1
