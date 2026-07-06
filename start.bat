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
    py --version >nul 2>nul
    if not errorlevel 1 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; sys.exit(0)" >nul 2>nul
        if not errorlevel 1 (
            set PYTHON_CMD=python
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
    echo   1. Installer Python depuis https://www.python.org/downloads/
    echo      IMPORTANT : cocher "Add Python to PATH" lors de l'installation
    echo   2. Ou desactiver l'alias Store :
    echo      Parametres ^> Applications ^> Alias d'execution ^> desactiver python.exe
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo [OK] %%i (commande: %PYTHON_CMD%)

REM ── 2. Node.js ───────────────────────────────────────────────────────────
node --version >nul 2>nul
if not errorlevel 1 goto node_ok

REM node absent du PATH, chercher manuellement
if exist "C:\Program Files\nodejs\node.exe" (
    set "PATH=C:\Program Files\nodejs;%PATH%"
    goto node_ok
)
if exist "C:\Program Files (x86)\nodejs\node.exe" (
    set "PATH=C:\Program Files (x86)\nodejs;%PATH%"
    goto node_ok
)
for %%D in (
    "%LOCALAPPDATA%\Programs\nodejs"
    "%APPDATA%\npm"
    "%USERPROFILE%\AppData\Roaming\nvm\latest"
) do (
    if exist "%%~D\node.exe" (
        set "PATH=%%~D;%PATH%"
        goto node_ok
    )
)

echo.
echo [ERREUR] Node.js introuvable.
echo   Installer depuis https://nodejs.org/ (version LTS)
echo   Puis relancer ce script.
echo.
pause
exit /b 1

:node_ok
for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node %%i

REM ── 3. Venv Python ───────────────────────────────────────────────────────
echo.
echo [1/4] Installation des dependances Python...

REM Supprimer le venv si requirements.txt a change (evite les conflits de versions)
if exist "%SCRIPT_DIR%backend\venv" (
    fc /b "%SCRIPT_DIR%backend\requirements.txt" "%SCRIPT_DIR%backend\venv\.requirements_hash" >nul 2>nul
    if errorlevel 1 (
        echo       Mise a jour des dependances detectee, reinitialisation du venv...
        rmdir /s /q "%SCRIPT_DIR%backend\venv"
    )
)

if not exist "%SCRIPT_DIR%backend\venv" (
    %PYTHON_CMD% -m venv "%SCRIPT_DIR%backend\venv"
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel.
        pause
        exit /b 1
    )
)

call "%SCRIPT_DIR%backend\venv\Scripts\activate.bat"

REM Upgrade pip silencieusement
python -m pip install --upgrade pip --quiet

REM Installer uniquement depuis wheels precompiles (--only-binary=:all:)
REM pour eviter toute compilation C (matplotlib, numpy, etc.)
pip install --only-binary=:all: -q -r "%SCRIPT_DIR%backend\requirements.txt"
if errorlevel 1 (
    echo.
    echo   Tentative avec les wheels standards...
    pip install -q -r "%SCRIPT_DIR%backend\requirements.txt"
    if errorlevel 1 (
        echo.
        echo [ERREUR] Installation des packages Python echouee.
        echo.
        echo   Cause probable : version de Python trop recente sans wheels disponibles.
        echo   Solution : installer Python 3.12 depuis https://www.python.org/downloads/
        echo   (choisir Python 3.12.x, la version la plus stable)
        echo.
        pause
        exit /b 1
    )
)

REM Sauvegarder l'empreinte du requirements pour detection de changements
copy /y "%SCRIPT_DIR%backend\requirements.txt" "%SCRIPT_DIR%backend\venv\.requirements_hash" >nul

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

start "" cmd /c "timeout /t 2 >nul & start http://localhost:8000"

cd "%SCRIPT_DIR%backend"
uvicorn main:app --host 127.0.0.1 --port 8000
