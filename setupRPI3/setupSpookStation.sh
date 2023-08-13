#!/bin/bash

# Update apt
sudo apt update

# Install dependencies for kivy
sudo apt -y install python3-setuptools git-core python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   libgstreamer1.0-dev \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} libmtdev-dev \
   xclip xsel libjpeg-dev 

# Remove old venv
sudo rm -r ../venv

# Install virtualenv
python3 -m pip install --upgrade pip setuptools virtualenv

# Create venv
python3 -m venv ../venv

# Activate venv
source ../venv/bin/activate

# Verify venv was activated
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "Virtual environment not activated"
    exit 1
fi

# Install kivy in venv
../venv/bin/python -m pip install kivy[base] kivy_examples paho-mqtt

# Install dependencies for Access Point
sudo apt install hostapd dnsmasq mosquitto mosquitto-clients

# Enable hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd

# Enable persistent iptables
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

# Append config to dhcpcd.conf
sudo cat setupConfigs/dhcpcd.conf >> /etc/dhcpcd.conf

# Backup dnsmasq.conf
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

# Copy dnsmasq.conf
sudo cp setupConfigs/dnsmasq.conf /etc/dnsmasq.conf

# Restart wireless service
sudo rfkill unblock wlan

# Copy hostapd.conf
sudo cp setupConfigs/hostapd.conf /etc/hostapd/hostapd.conf

# Copy mosquitto.conf
sudo cp setupConfigs/mosquitto.conf /etc/mosquitto/conf.d/mosquitto.conf

# Restart mosquitto service
sudo service mosquitto restart

echo "To run the GUI, activate the virtual environment with 'source ./venv/bin/activate' and run 'python main.py' or simply run runGuiUbuntu.sh"
echo "Please reboot the Raspberry Pi for changes to take effect"