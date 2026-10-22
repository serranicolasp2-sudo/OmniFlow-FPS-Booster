@echo off
title PixarFlow FPS Booster
cd /d "%~dp0"
start "" pythonw app_fps_booster.py
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando con consola...
    python app_fps_booster.py
    pause
)
