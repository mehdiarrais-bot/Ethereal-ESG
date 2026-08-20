@echo off
REM ---------------------------------------------------------
REM  Ethereal ESG - Lancement rapide
REM  (lancer install.bat d'abord si premiere utilisation)
REM ---------------------------------------------------------
title Ethereal ESG

set SCRIPT_DIR=%~dp0

REM ── Verifier que l'installation a ete faite ───────────────
if not exist "%SCRIPT_DIR%backend\venv\Scripts\uvicorn.exe" (
    echo.
    echo   Installation requise. Lancement de install.bat...
    echo.
    call "%SCRIPT_DIR%install.bat"
    if errorlevel 1 ( pause & exit /b 1 )
)

REM ── Verifier si requirements ont change ──────────────────
fc /b "%SCRIPT_DIR%backend\requirements.txt" "%SCRIPT_DIR%backend\venv\.req_hash" >nul 2>nul
if errorlevel 1 (
    echo Mise a jour des dependances Python...
    call "%SCRIPT_DIR%backend\venv\Scripts\activate.bat"
    pip install --only-binary=:all: -q -r "%SCRIPT_DIR%backend\requirements.txt" >nul 2>nul
    pip install -q -r "%SCRIPT_DIR%backend\requirements.txt" >nul 2>nul
    copy /y "%SCRIPT_DIR%backend\requirements.txt" "%SCRIPT_DIR%backend\venv\.req_hash" >nul
)

REM ── Lancement ─────────────────────────────────────────────
echo.
echo   Ethereal ESG - Demarrage...
echo   URL : http://localhost:8000
echo.
echo   Ctrl+C pour arreter.
echo.

start "" cmd /c "timeout /t 2 >nul & start http://localhost:8000"

call "%SCRIPT_DIR%backend\venv\Scripts\activate.bat"
cd "%SCRIPT_DIR%backend"
uvicorn main:app --host 127.0.0.1 --port 8000
