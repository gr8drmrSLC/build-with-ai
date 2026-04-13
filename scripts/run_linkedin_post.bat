@echo off
REM run_linkedin_post.bat
REM Wrapper called by Windows Task Scheduler.
REM Tries job-search venv first, falls back to system Python.

set PROJECT_DIR=C:\Users\V2Rst\build-with-ai
set SCRIPT=%PROJECT_DIR%\scripts\post_linkedin_daily.py
set LOG=%PROJECT_DIR%\scripts\linkedin_post.log
set VENV_PY=%USERPROFILE%\job-search\venv\Scripts\python.exe

echo. >> "%LOG%"
echo ===== %DATE% %TIME% ===== >> "%LOG%"

if exist "%VENV_PY%" (
    echo Using job-search venv >> "%LOG%"
    "%VENV_PY%" "%SCRIPT%" >> "%LOG%" 2>&1
) else (
    echo Using system Python >> "%LOG%"
    python "%SCRIPT%" >> "%LOG%" 2>&1
)

if %ERRORLEVEL% NEQ 0 (
    echo FAILED with exit code %ERRORLEVEL% >> "%LOG%"
) else (
    echo SUCCESS >> "%LOG%"
)
