@echo off
cd /d "%~dp0"
if exist "python_win\pythonw.exe" (
    start "" "python_win\pythonw.exe" yen.py
    exit /b
)
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python nao encontrado. Instalando automaticamente via Winget...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
)
start "" pythonw yen.py || python yen.py
