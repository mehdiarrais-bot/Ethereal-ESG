@echo off
REM ---------------------------------------------------------
REM  Ethereal ESG - Installation (a faire UNE SEULE FOIS)
REM ---------------------------------------------------------
title Ethereal ESG - Installation

echo.
echo   Ethereal ESG - Installation initiale
echo   =====================================
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_CMD=

REM ── Detecter Python ──────────────────────────────────────
where py >nul 2>nul
if not errorlevel 1 ( py --version >nul 2>nul && set PYTHON_CMD=py )
if "%PYTHON_CMD%"=="" ( python -c "import sys;sys.exit(0)" >nul 2>nul && set PYTHON_CMD=python )
if "%PYTHON_CMD%"=="" ( where python3 >nul 2>nul && set PYTHON_CMD=python3 )
if "%PYTHON_CMD%"=="" (
    echo [ERREUR] Python introuvable. Installer depuis https://www.python.org/downloads/
    echo Cocher "Add Python to PATH"
    pause & exit /b 1
)
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo [OK] %%i

REM ── Detecter Node ────────────────────────────────────────
node --version >nul 2>nul
if not errorlevel 1 goto node_ok
if exist "C:\Program Files\nodejs\node.exe" ( set "PATH=C:\Program Files\nodejs;%PATH%" & goto node_ok )
if exist "C:\Program Files (x86)\nodejs\node.exe" ( set "PATH=C:\Program Files (x86)\nodejs;%PATH%" & goto node_ok )
echo [ERREUR] Node.js introuvable. Installer depuis https://nodejs.org/ puis relancer.
pause & exit /b 1
:node_ok
for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node %%i

REM ── Venv Python ──────────────────────────────────────────
echo.
echo [1/3] Installation des dependances Python...
if exist "%SCRIPT_DIR%backend\venv" ( rmdir /s /q "%SCRIPT_DIR%backend\venv" )
%PYTHON_CMD% -m venv "%SCRIPT_DIR%backend\venv"
call "%SCRIPT_DIR%backend\venv\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet
pip install --only-binary=:all: -q -r "%SCRIPT_DIR%backend\requirements.txt"
if errorlevel 1 (
    pip install -q -r "%SCRIPT_DIR%backend\requirements.txt"
    if errorlevel 1 ( echo [ERREUR] pip install echoue. & pause & exit /b 1 )
)
copy /y "%SCRIPT_DIR%backend\requirements.txt" "%SCRIPT_DIR%backend\venv\.req_hash" >nul
echo [OK] Dependances Python installees

REM ── Node modules ─────────────────────────────────────────
echo [2/3] Installation des dependances Node...
cd "%SCRIPT_DIR%frontend"
call npm install --silent
if errorlevel 1 ( echo [ERREUR] npm install echoue. & pause & exit /b 1 )
copy /y "%SCRIPT_DIR%frontend\package.json" "%SCRIPT_DIR%frontend\node_modules\.pkg_hash" >nul
echo [OK] Dependances Node installees

REM ── Build frontend ────────────────────────────────────────
echo [3/3] Compilation du frontend...
call npm run build --silent
if errorlevel 1 ( echo [ERREUR] Build echoue. & pause & exit /b 1 )
echo [OK] Frontend compile

echo.
echo   ============================================
echo   Installation terminee !
echo   Lancez l'app avec start.bat
echo   ============================================
echo.
pause
