echo off

cd /D "%~dp0"

REM Prompt for admin privileges
NET FILE >NUL 2>NUL
if '%errorlevel%' == '0' (
    echo "Running with administrative privileges..."
) else (
    echo "Please run this script as an administrator."
    pause
    exit /b 1
)

REM Check if venv already exists
if exist %~dp0venv\ (
    echo "Please delete the existing venv folder and run this script again."
    pause
    exit /b 1
) 

REM Check if mosquitto service is installed
sc query mosquitto >nul
if %errorlevel% equ 1060 (
    echo "Mosquitto service not found, Please install mosquitto MQTT broker from https://mosquitto.org/download/"
    pause
    exit 1
)

REM Get the mosquitto service executable path
for /f "tokens=*" %%a in ('sc qc mosquitto ^| findstr "BINARY_PATH_NAME"') do set "mosquitto_exe_path=%%a"
set "mosquitto_exe_path=%mosquitto_exe_path:~22,-5%"
echo "Mosquitto service executable path: %mosquitto_exe_path%"

REM Get the mosquitto service executable folder
for %%i in ("%mosquitto_exe_path%") do set mosquitto_exe_folder=%%~dpi
echo "Mosquitto service executable folder: %mosquitto_exe_folder%"

REM Stop mosquitto service
net stop mosquitto

REM Remove mosquitto.conf and acl.acl files from mosquitto service folder
if exist "%mosquitto_exe_folder%mosquitto.conf" (
    echo "Deleting existing mosquitto.conf file..."
    del "%mosquitto_exe_folder%mosquitto.conf"
)
if exist "%mosquitto_exe_folder%acl.acl" (
    echo "Deleting existing acl.acl file..."
    del "%mosquitto_exe_folder%acl.acl"
)

REM Create mosquitto.conf file in mosquitto service folder
echo "Creating mosquitto.conf file..."
echo. >> "%mosquitto_exe_folder%mosquitto.conf"
echo sys_interval 1 >> "%mosquitto_exe_folder%mosquitto.conf"
echo allow_anonymous true >> "%mosquitto_exe_folder%mosquitto.conf"
echo acl_file %mosquitto_exe_folder%acl.acl >> "%mosquitto_exe_folder%mosquitto.conf"

REM Create acl.acl file in mosquitto service folder
echo "Creating acl.acl file..."
echo. >> "%mosquitto_exe_folder%acl.acl"
echo topic read # >> "%mosquitto_exe_folder%acl.acl"
echo topic write # >> "%mosquitto_exe_folder%acl.acl"
echo topic read $SYS/# >> "%mosquitto_exe_folder%acl.acl"

REM Start mosquitto service
net start mosquitto

python -m pip install --upgrade pip setuptools virtualenv

REM Create a virtual environment and activate it
python -m venv venv
call venv\Scripts\activate.bat

REM verify that the venv is activated
if "%VIRTUAL_ENV%" == "" (
    echo "ERROR: virtual environment is not activated"
    pause
    exit 1
 )

REM Install the required packages
%~dp0venv\Scripts\python.exe -m pip install --upgrade pip
%~dp0venv\Scripts\python.exe -m pip install -r requirements.txt

echo:
echo "If you wish to run the GUI from Visual studio code, select the interpreter from the venv folder"
echo "To run the GUI, run the command: runGuiWindows.bat"

pause