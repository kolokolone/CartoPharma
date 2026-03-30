@echo off
setlocal EnableExtensions

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%" || goto :fail

set "VENV_DIR=%PROJECT_DIR%.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "LOG_DIR=%PROJECT_DIR%data\logs"

if /i "%~1"=="--smoke" goto :smoke

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

if not exist "%PYTHON_EXE%" (
    echo [INFO] Creation de l'environnement virtuel...
    py -3 -m venv "%VENV_DIR%" 2>nul || python -m venv "%VENV_DIR%"
    if errorlevel 1 goto :fail
)

where node >nul 2>&1 || goto :node_missing
where npm >nul 2>&1 || goto :node_missing

echo [INFO] Lancement du backend CartoPharma...
start "CartoPharma Backend" /D "%PROJECT_DIR%" cmd /k "call start_backend.bat"

echo [INFO] Attente du healthcheck backend...
powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(45); do { try { $r=Invoke-WebRequest 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 echo [WARN] Backend non pret apres 45s. Le frontend sera quand meme lance.

echo [INFO] Lancement du frontend CartoPharma...
start "CartoPharma Frontend" /D "%PROJECT_DIR%" cmd /k "call start_frontend.bat"

echo [INFO] Ouverture du navigateur: http://localhost:3000
start "" "http://localhost:3000"

echo.
echo [INFO] Deux fenetres ont ete lancees (Backend + Frontend).
pause
endlocal
exit /b 0

:smoke
where node >nul 2>&1 || goto :node_missing
where npm >nul 2>&1 || goto :node_missing
if not exist "%PROJECT_DIR%backend\requirements.txt" (
    echo [SMOKE][ERREUR] backend\requirements.txt introuvable
    goto :fail
)
if not exist "%PROJECT_DIR%frontend\package.json" (
    echo [SMOKE][ERREUR] frontend\package.json introuvable
    goto :fail
)
echo [SMOKE] OK
endlocal
exit /b 0

:node_missing
echo [ERREUR] Node.js (node/npm) introuvable.
pause
endlocal
exit /b 1

:fail
echo.
echo [ERREUR] Le script a echoue.
pause
endlocal
exit /b 1
