echo off

if not exist %~dp0venv\ (
    echo "Please run setupDevEnvironmentWindows.bat first"
    pause
    exit 1
) 

call venv\Scripts\activate.bat

:: verify that the venv is activated
if "%VIRTUAL_ENV%" == "" (
    echo "ERROR: virtual environment is not activated"
    pause
    exit 1
 )

:: Run the GUI
%~dp0venv\Scripts\python.exe %~dp0SpookStationGui\main.py
