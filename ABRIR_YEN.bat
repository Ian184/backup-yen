@echo off
cd /d "%~dp0"
start "" pythonw yen.py || python yen.py
