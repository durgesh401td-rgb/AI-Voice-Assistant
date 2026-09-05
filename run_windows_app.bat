@echo off
title Launching Aura Windows AI Assistant
echo =======================================================
echo     AURA // Autonomous Windows Voice AI Assistant
echo =======================================================
echo.
cd /d "%~dp0"
echo Installing requirements...
python -m pip install -r requirements.txt
echo.
echo Starting Windows Desktop Application...
python windows_app.py
pause