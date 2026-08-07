@echo off
cd /d "%~dp0.."
setlocal enabledelayedexpansion

REM Read version from version.py
for /f "tokens=3 delims= " %%a in ('findstr /b "VERSION" version.py') do (
    set VER=%%a
)
set VER=%VER:"=%
if "%VER%"=="" (
    echo ERROR: Could not read version from version.py
    exit /b 1
)
echo ============================================
echo  Building Transcripty %VER%
echo ============================================
echo.

REM Step 1: Generate logo assets
echo [1/4] Generating logo assets...
python logo_source.py
if %errorlevel% neq 0 (
    echo ERROR: Logo generation failed with code %errorlevel%
    exit /b %errorlevel%
)
echo Done.
echo.

REM Step 2: Clean previous builds
echo [2/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist "dist\Transcripty" rmdir /s /q dist\Transcripty
if exist "Transcripty_v%VER%_Setup.exe" del "Transcripty_v%VER%_Setup.exe"
if exist "Transcripty_v%VER%_Installer.exe" del "Transcripty_v%VER%_Installer.exe"
echo Done.
echo.

REM Step 3: PyInstaller
echo [3/4] Running PyInstaller...
pyinstaller Transcripty.spec
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller failed with code %errorlevel%
    exit /b %errorlevel%
)
echo Done.
echo.

REM Step 4: Inno Setup
echo [4/4] Running Inno Setup...
iscc /DMyAppVersion="%VER%" setup.iss
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup failed with code %errorlevel%
    exit /b %errorlevel%
)
echo Done.
echo.

echo ============================================
echo  SUCCESS: Transcripty_v%VER%_Setup.exe
echo ============================================
