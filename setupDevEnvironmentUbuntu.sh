#!/bin/bash

# Update apt
sudo apt update

# Install dependencies for kivy
sudo apt -y install python3-setuptools git-core python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   libgstreamer1.0-dev \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   libmtdev-dev \
   xclip xsel libjpeg-dev python3-venv mosquitto mosquitto-clients

# Check if venv already exists
if [ -d "./venv" ]
then
    # Remove old venv
    sudo rm -r ./venv
fi

# Install virtualenv
python3 -m pip install --upgrade pip setuptools virtualenv

# Create venv
python3 -m venv ./venv

# Activate venv
source ./venv/bin/activate

# Verify venv was activated
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "Virtual environment not activated"
    exit 1
fi

# Install kivy in venv
./venv/bin/python -m pip install -r requirements.txt

echo "Setup complete"
echo "If you wish to run the GUI from Visual studio code, select the interpreter /venv/Scripts/python"
echo "To run the GUI, run the command: 'bash runGuiUbuntu.sh'"