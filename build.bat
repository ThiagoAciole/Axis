@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

:: ============================================================
:: 🚀 Build completo do Axis (com assets, logo e ícone)
:: ============================================================
set "APP_NAME=Axis"
set "ROOT_DIR=C:\Source"
set "BASE_DIR=%ROOT_DIR%\%APP_NAME%"
cd /d "%BASE_DIR%"

echo.
echo ============================================================
echo   🚀 Iniciando build do Axis...
echo ============================================================
echo.

:: Caminhos principais
set "ICON_PATH=%BASE_DIR%\app\assets\icon.ico"
set "LOGO_PATH=%BASE_DIR%\app\assets\logo.png"
set "MAIN_FILE=%BASE_DIR%\app\main.py"

:: Saídas
set "BUILD_PATH=%BASE_DIR%\build"
set "DIST_PATH=%BASE_DIR%\dist"
set "RELEASE_PATH=%BASE_DIR%\release"
set "OUTPUT_EXE=%RELEASE_PATH%\%APP_NAME%.exe"

:: ============================================================
:: 🧹 Limpeza inicial
:: ============================================================
echo 🧹 Limpando builds anteriores...
if exist "%BUILD_PATH%" rd /s /q "%BUILD_PATH%"
if exist "%DIST_PATH%" rd /s /q "%DIST_PATH%"
if exist "%RELEASE_PATH%" rd /s /q "%RELEASE_PATH%"
if exist "%BASE_DIR%\OneLauncher.spec" del /f /q "%BASE_DIR%\OneLauncher.spec"
pyinstaller --clean >nul 2>&1

:: ============================================================
:: 🧩 Verificações básicas
:: ============================================================
if not exist "%ICON_PATH%" (
    echo ❌ ERRO: Ícone não encontrado: "%ICON_PATH%"
    pause
    exit /b 1
)

if not exist "%LOGO_PATH%" (
    echo ❌ ERRO: Logo não encontrada: "%LOGO_PATH%"
    pause
    exit /b 1
)

if not exist "%MAIN_FILE%" (
    echo ❌ ERRO: main.py não encontrado: "%MAIN_FILE%"
    pause
    exit /b 1
)

:: ============================================================
:: 🏗️ Compilando com PyInstaller
:: ============================================================
echo 🏗️  Gerando executável...

pyinstaller ^
 --noconfirm ^
 --clean ^
 --onefile ^
 --windowed ^
 --name "%APP_NAME%" ^
 --icon "%ICON_PATH%" ^
 --distpath "%DIST_PATH%" ^
 --workpath "%BUILD_PATH%" ^
 --specpath "%BUILD_PATH%" ^
 --add-data "%BASE_DIR%\app\assets;app/assets" ^
 --add-data "%BASE_DIR%\app\assets\icons;app/assets/icons" ^
 --add-data "%BASE_DIR%\app\assets\icons\buttons;app/assets/icons/buttons" ^
 --add-data "%BASE_DIR%\app\settings;app/settings" ^
 --add-data "%BASE_DIR%\app\ui;app/ui" ^
 --add-data "%BASE_DIR%\app\utils;app/utils" ^
 "%MAIN_FILE%"

:: ============================================================
:: 📦 Mover dist -> release
:: ============================================================
if exist "%DIST_PATH%" (
    echo 📦 Movendo pasta dist -> release...
    if exist "%RELEASE_PATH%" rd /s /q "%RELEASE_PATH%"
    move "%DIST_PATH%" "%RELEASE_PATH%" >nul
)

:: ============================================================
:: 🧽 Limpeza final
:: ============================================================
if exist "%BASE_DIR%\%APP_NAME%.spec" del /f /q "%BASE_DIR%\%APP_NAME%.spec"
if exist "%BUILD_PATH%" rd /s /q "%BUILD_PATH%"

:: ============================================================
:: ✅ Resultado final
:: ============================================================
if exist "%OUTPUT_EXE%" (
    echo.
    echo ✅ Build concluído com sucesso!
    echo 📁 Executável criado em:
    echo     "%OUTPUT_EXE%"
) else (
    echo.
    echo ❌ ERRO: Executável não foi criado.
)

echo.
pause
endlocal
