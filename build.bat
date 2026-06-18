@echo off
echo Processing logo...
python process_logo.py
if %errorlevel% neq 0 (
    echo Logo processing FAILED.
    pause
    exit /b 1
)

echo Cleaning previous build...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist ReadMi.spec del /q ReadMi.spec

echo Building ReadMi v3.0.0...
python -m PyInstaller --onefile --windowed --add-data "web;web" --icon=readmi.ico --name ReadMi main.py

if %errorlevel% neq 0 (
    echo Build FAILED.
    pause
    exit /b 1
)

echo.
echo Build complete: dist\ReadMi.exe
pause
