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
echo  Building Transcript %VER%
echo ============================================
echo.

REM Step 1: Clean previous builds
echo [1/3] Cleaning previous builds...
if exist build rmdir /s /q build
if exist "dist\Transcript" rmdir /s /q dist\Transcript
if exist "Transcript_v%VER%_Setup.exe" del "Transcript_v%VER%_Setup.exe"
if exist "Transcript_v%VER%_Installer.exe" del "Transcript_v%VER%_Installer.exe"
echo Done.
echo.

REM Step 2: PyInstaller
echo [2/3] Running PyInstaller...
pyinstaller Transcript.spec
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller failed with code %errorlevel%
    exit /b %errorlevel%
)
echo Done.
echo.

REM Step 3: Inno Setup
echo [3/3] Running Inno Setup...
iscc /DMyAppVersion="%VER%" setup.iss
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup failed with code %errorlevel%
    exit /b %errorlevel%
)
echo Done.
echo.

echo ============================================
echo  SUCCESS: Transcript_v%VER%_Setup.exe
echo ============================================
