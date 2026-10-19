@echo off
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" -B -m demo.phone --stop
if errorlevel 1 pause
