@echo off
REM ---------------------------------------------------------
REM  ESG Platform - Demarrage local (Windows)
REM  Double-cliquer sur ce fichier pour lancer l'app
REM ---------------------------------------------------------

title ESG Platform

echo.
echo   ESG Platform - Generateur de rapports ESG / RSE
echo   100%% Local - Aucune API requise
echo   ================================================
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_CMD=

REM ── 1. Detecter Python (py launcher, puis python, puis python3) ──────────
where py >nul 2>nul
if not errorlevel 1 (
    REM Verifier que "py" pointe vers un vrai Python (pas le Store)
    py --version >nul 2>nul
    if not errorlevel 1 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 (
        REM Verifier que "python" n'est pas l'alias Microsoft Store
        python --version >nul 2>nul
        if not errorlevel 1 (
            REM Tester si c'est le vrai Python (le Store retourne errorlevel 9009)
            python -c "import sys; sys.exit(0)" >nul 2>nul
            if not errorlevel 1 (
                set PYTHON_CMD=python
            )
        )
    )
)

if "%PYTHON_CMD%"=="" (
    where python3 >nul 2>nul
    if not errorlevel 1 (
        set PYTHON_CMD=python3
    )
)

if "%PYTHON_CMD%"=="" (
    echo.
    echo [ERREUR] Python 3 introuvable.
    echo.
    echo Solutions :
    echo   1. Installer Python depuis https://www.python.org/downloads/
    echo      IMPORTANT : cocher "Add Python to PATH" lors de l'installation
    echo   2. Ou desactiver l'alias Store : Parametres ^> Applications ^>
    echo      Alias d'execution d'applications ^> desactiver python.exe
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo [OK] %%i (commande: %PYTHON_CMD%)

REM ── 2. Node.js ───────────────────────────────────────────────────────────
where node >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERREUR] Node.js introuvable.
    echo.
    echo Installer Node.js depuis https://nodejs.org/
    echo Choisir la version LTS, puis relancer ce script.
    echo.
    echo Si Node.js est deja installe, fermer et rouvrir cette fenetre
    echo pour recharger le PATH.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node %%i

REM ── 3. Venv Python ───────────────────────────────────────────────────────
echo.
echo [1/4] Installation des dependances Python...
if not exist "%SCRIPT_DIR%backend\venv" (
    %PYTHON_CMD% -m venv "%SCRIPT_DIR%backend\venv"
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel.
        pause
        exit /b 1
    )
)
call "%SCRIPT_DIR%backend\venv\Scripts\activate.bat"
pip install -q -r "%SCRIPT_DIR%backend\requirements.txt"
if errorlevel 1 (
    echo [ERREUR] Installation des packages Python echouee.
    pause
    exit /b 1
)
echo [OK] Dependances Python installees

REM ── 4. Node modules ──────────────────────────────────────────────────────
echo [2/4] Installation des dependances Node...
cd "%SCRIPT_DIR%frontend"
call npm install --silent
if errorlevel 1 (
    echo [ERREUR] npm install echoue.
    pause
    exit /b 1
)
echo [OK] Dependances Node installees

REM ── 5. Build frontend ────────────────────────────────────────────────────
echo [3/4] Compilation du frontend...
call npm run build --silent
if errorlevel 1 (
    echo [ERREUR] Build frontend echoue.
    pause
    exit /b 1
)
echo [OK] Frontend compile

REM ── 6. Demarrage ─────────────────────────────────────────────────────────
echo [4/4] Demarrage...
echo.
echo   L'application va s'ouvrir dans votre navigateur.
echo   URL : http://localhost:8000
echo.
echo   Fermer cette fenetre pour arreter l'application.
echo.

REM Ouvrir le navigateur apres 2 secondes
start "" cmd /c "timeout /t 2 >nul & start http://localhost:8000"

cd "%SCRIPT_DIR%backend"
uvicorn main:app --host 127.0.0.1 --port 8000
