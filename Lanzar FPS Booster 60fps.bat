@echo off
title PixarFlow 60fps
cd /d "%~dp0"
start "" pythonw app_fps_booster.py
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando con consola...
    python app_fps_booster.py
    pause
)
