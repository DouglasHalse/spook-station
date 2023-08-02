#!/bin/bash

echo "Installing hostapd..."
sudo apt install hostapd
echo "hostapd installed."

echo "Enabling hostapd..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
echo "hostapd enabled."

echo "Installing dnsmasq..."
sudo apt install dnsmasq
echo "dnsmasq installed"

echo "Installing netfilter-persistent iptables-persistent..."
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
echo "netfilter-persistent iptables-persistent installed"

echo "Adding config to /etc/dhcpcd.conf..."
sudo cat setupConfigs/dhcpcd.conf >> /etc/dhcpcd.conf
echo "Added config to /etc/dhcpcd.conf"

echo "Creating backup for /etc/dnsmasq.conf..."
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
echo "Created backuip for /etc/dnsmasq.conf"

echo "Copying setupConfigs/dnsmasq.conf to /etc/dnsmasq.conf..."
sudo cp setupConfigs/dnsmasq.conf /etc/dnsmasq.conf
echo "Copied setupConfigs/dnsmasq.conf to /etc/dnsmasq.conf"

echo "Restarting wireless service..."
sudo rfkill unblock wlan
echo "Restarted wireless service"

echo "Copying setupConfigs/hostapd.conf to /etc/hostapd/hostapd.conf..."
sudo cp setupConfigs/hostapd.conf /etc/hostapd/hostapd.conf
echo "Copied setupConfigs/hostapd.conf to /etc/hostapd/hostapd.conf"

echo "Copying setupConfigs/mosquitto.conf to /etc/mosquitto/conf.d/mosquitto.conf"
sudo cp setupConfigs/mosquitto.conf /etc/mosquitto/conf.d/mosquitto.conf
echo "Copied setupConfigs/mosquitto.conf to /etc/mosquitto/conf.d/mosquitto.conf"

echo "Restarting mosquitto service..."
sudo service mosquitto restart
echo "Mosquitto service restarted"

echo "Please reboot the Raspberry Pi for changes to take effect"
