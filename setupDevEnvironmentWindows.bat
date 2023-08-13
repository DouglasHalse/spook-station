echo off

if exist %~dp0venv\ (
    echo "Please delete the existing venv folder"
    pause
    exit 1
) 

pip install --upgrade pip setuptools virtualenv

:: create a virtual environment and activate it
python -m venv venv
call venv\Scripts\activate.bat

:: verify that the venv is activated
if "%VIRTUAL_ENV%" == "" (
    echo "ERROR: virtual environment is not activated"
    pause
    exit 1
 )

:: Install the required packages
%~dp0venv\Scripts\python.exe -m pip install --upgrade pip
%~dp0venv\Scripts\python.exe -m pip install -r requirements.txt

echo:
echo "Please install mosquitto MQTT broker from https://mosquitto.org/download/"
echo "If you wish to run the GUI from Visual studio code, select the interpreter from the venv folder"
echo "To run the GUI, run the command: runGuiWindows.bat"

pause