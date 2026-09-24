@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py validate_distribution.py
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python validate_distribution.py
    exit /b %ERRORLEVEL%
)

echo.
echo Python was not found on PATH.
echo Install Python or ask your collaborator to use the repo's virtual environment.
exit /b 1
