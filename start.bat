@echo off
REM ─────────────────────────────────────────────────────────
REM  ESG Platform — Démarrage local (Windows)
REM  Double-cliquer sur ce fichier pour lancer l'app
REM ─────────────────────────────────────────────────────────

title ESG Platform

echo.
echo   ESG Platform — Generateur de rapports ESG / RSE
echo   100%% Local - Aucune API requise
echo   ================================================
echo.

set SCRIPT_DIR=%~dp0

REM ── 1. Python ────────────────────────────────────────────
where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python non trouve.
    echo Installer depuis https://www.python.org/downloads/
    echo Cocher "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i

REM ── 2. Node.js ───────────────────────────────────────────
where node >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Node.js non trouve.
    echo Installer depuis https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo [OK] Node %%i

REM ── 3. Venv Python ───────────────────────────────────────
echo.
echo [1/4] Installation des dependances Python...
if not exist "%SCRIPT_DIR%backend\venv" (
    python -m venv "%SCRIPT_DIR%backend\venv"
)
call "%SCRIPT_DIR%backend\venv\Scripts\activate.bat"
pip install -q -r "%SCRIPT_DIR%backend\requirements.txt"
echo [OK] Dependances Python installees

REM ── 4. Node modules ──────────────────────────────────────
echo [2/4] Installation des dependances Node...
cd "%SCRIPT_DIR%frontend"
call npm install --silent
echo [OK] Dependances Node installees

REM ── 5. Build frontend ────────────────────────────────────
echo [3/4] Compilation du frontend...
call npm run build --silent
echo [OK] Frontend compile

REM ── 6. Démarrage ─────────────────────────────────────────
echo [4/4] Demarrage...
echo.
echo   L'application va s'ouvrir dans votre navigateur.
echo   URL : http://localhost:8000
echo.
echo   Fermer cette fenetre pour arreter l'application.
echo.

REM Ouvrir le navigateur après 2 secondes
start "" timeout /t 2 >nul & start http://localhost:8000

cd "%SCRIPT_DIR%backend"
uvicorn main:app --host 127.0.0.1 --port 8000
