@echo off
REM ======================================================
REM  BahtBuddy Deployment Package - Build Script
REM  Author: Thanakrit (Pass) Punyasuntontamrong
REM  Description: Builds and launches BahtBuddy GUI executable
REM ======================================================

echo 🚀 Checking Python environment...

REM Use python -m pip to avoid "pip not recognized" issues
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pyinstaller >nul 2>&1

if errorlevel 1 (
    echo ❌ Failed to install PyInstaller. Please verify Python is installed.
    pause
    exit /b
)

echo ✅ PyInstaller ready. Building BahtBuddy.exe...

REM Change to main directory (parent of deployment_package)
cd /d "%~dp0.."

REM Clean previous builds
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM Build executable from GUI
python -m PyInstaller --onefile --noconsole gui.py --name "BahtBuddy"

REM Check for success
if exist "dist\BahtBuddy.exe" (
    echo ✅ Build complete!
    echo.
    echo Launching BahtBuddy GUI...
    start "" "dist\BahtBuddy.exe"
) else (
    echo ❌ Build failed — executable not found.
)

pause
