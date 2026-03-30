@echo off
setlocal EnableExtensions

cd /d "%~dp0" || goto :fail

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%BACKEND_DIR%\requirements.txt" (
  echo [ERROR] Missing backend\requirements.txt
  goto :fail
)

if not exist "%PY%" (
  echo [INFO] Creating virtual environment: "%VENV_DIR%"
  py -3 -m venv "%VENV_DIR%" 2>nul || python -m venv "%VENV_DIR%"
  if errorlevel 1 goto :fail
)

echo [INFO] Installing backend dependencies...
"%PY%" -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 goto :fail

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
  echo [WARN] Existing listener detected on :8000 pid=%%a, stopping it...
  taskkill /F /PID %%a >nul 2>&1
)

set "RELOAD_ARGS="
if /i "%CARTOPHARMA_RELOAD%"=="1" set "RELOAD_ARGS=--reload"

pushd "%BACKEND_DIR%" || goto :fail
echo [INFO] Starting backend: http://127.0.0.1:8000
"%PY%" -m uvicorn app.main:app %RELOAD_ARGS% --host 127.0.0.1 --port 8000
if errorlevel 1 goto :fail

popd
endlocal
exit /b 0

:fail
echo.
echo [ERROR] Backend launch failed.
pause
popd >nul 2>&1
endlocal
exit /b 1
