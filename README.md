# Spook station
Spook station is a role-playing tool controlling ghost-hunting equipment wirelessly.
The idea is to have real-life ghost-hunting-like equipment used by the players that are remotely controlled by the game organizer (or Dungeon master).
The Dungeon master can trigger behaviors in the devices in correspondence to events in the game.

## Setup development environment
(If you are trying to follow these steps for the first time, PLEASE let us know if you run into any problems so we can update the setup process)
### Windows
#### Prerequisites
1. Python 3.9 (preferably installed from the Microsoft store)
2. Mosquitto MQTT broker (https://mosquitto.org/download/)
3. git (https://git-scm.com/download/win)

####  Recommended dev-tools
1. GitHub Desktop if you prefer GUI for git (https://desktop.github.com/)
2. Visual Studio Code (https://code.visualstudio.com/)

#### Installation
1. Clone this repository to your Windows machine using git
2. Run setupDevEnvironmentWindows.bat

#### Start GUI with debugging (with Visual Studio Code)
1. In Visual Studio Code: Select 'Open Folder...' and select the cloned repository
2. Hit Ctrl + Shift + P and write 'select interpreter' and click 'Python: Select Interpreter'
3. Select the Python executable found in \<cloned repository\>/venv/Scripts/python.exe
4. Open the main GUI python file in Visual Studio Code: \<cloned repository\>/SpookStation/SpookStationGui/main.py
5. Hit F5 to start debugging

#### Start GUI without debugging
1. Run runGuiWindows.bat

### Ubuntu
#### Prerequisites
1. Python 3.9 or Python 3.10

####  Recommended dev-tools
1. GitKraken Client if you prefer GUI for git (https://www.gitkraken.com/)
2. Visual Studio Code (https://code.visualstudio.com/)

#### Installation
[//]: <> (<area>-tag to escape hyper-link creation)
1. Clone this repository to your Ubuntu machine using git
2. Run 'bash setupDevEnvironmentUbuntu.<area>sh'

#### Start GUI with debugging (with Visual Studio Code)
1. In Visual Studio Code: Select 'Open Folder...' and select the cloned repository
2. Hit Ctrl + Shift + P and write 'select interpreter' and click 'Python: Select Interpreter'
3. Select the Python executable found in \<cloned repository\>/venv/Scripts/python
4. Open the main GUI python file in Visual Studio Code: \<cloned repository\>/SpookStation/SpookStationGui/main.py
5. Hit F5 to start debugging

#### Start GUI without debugging
[//]: <> (<area>-tag to escape hyper-link creation)
1. Run 'bash runGuiUbuntu.<area>sh'

## The Hardware
There are two types of hardware involved in this project: The Spook station and the devices.

### The Spook station
The device known as the spook station, is a Raspberry Pi 3B+ enclosed in a touchscreen case.
One or more devices connect to the Raspberry Pi's access point and connect to the locally hosted MQTT server on the Raspberry Pi. 
The main device runs a touchscreen GUI based on KIVY and sens control commands to the connected devices. 

### The devices
Devices automatically connect to the spook station and start listening for control signals and publish state signals. 
The communication used is MQTT over locally hosted access point so there are no requirements for what hardware is used for the devices.

#### EMFReader
Currently, we only support a modified EMFReader that has been modified to be controlled by an ESP32-S2 microcontroller instead of the actual electromagnetic frequency sensing equipment.
The EMFReader automatically connects to the spook station and can be controlled through the GUI.

<img src="images/EMFReader.gif" width="30%" />

##### Features:
The following can be controlled from the spook station:
1.  How many lights should be lit up
2.  Select the fluctuation magnitude
    * Select how much the lights fluctuate from the selected number of lights from (1.)
3. Select how fast the lights should fluctuate
4. Select if there should be sound played on the EMFReader when EMF levels 4 and 5 is detected

#### SpiritBox
The GUI implementation is not done yet for SpiritBox. The SpiritBox uses Raspberry Pi Zero 2W. 
##### Features:
The following can be controlled from the spook station:
1.  Set speech volume level
2.  Set speech rate
    * How fast the voice should be
3. Say sentence/word
    * The voice is synthesized to the connected speaker on the Raspberry Pi zero 2W
4. Set language
5. Set background static volume
6. Set static volume while speaking

#### Flashlight
No work has been done on the flashlight implementation yet
