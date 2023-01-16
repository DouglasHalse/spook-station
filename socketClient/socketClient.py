import socketserver
import threading
import subprocess
import time
import socket
import sys 
from abc import ABC, abstractmethod

class DeviceInfoBase(ABC):
	def __init__(self, deviceType, deviceName, deviceAddress, lastHeartBeat):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((deviceAddress, 80))
		self.socketLock = threading.Lock()
		self.running = True
		self.deviceType = deviceType
		self.deviceName = deviceName
		self.deviceAddress = deviceAddress
		self.requestHeartBeatTimer = threading.Timer(0.5, self.requestHeartBeat)
		self.connectionStatus = "none"
		self.lastHeartBeat = lastHeartBeat
		
	def __del__(self):
		#print("Destructing DeviceInfoBase")
		self.requestHeartBeatTimer.cancel()
		with self.socketLock:
			self.socket.close()
		
	def shutdownDevice(self):
		self.running = False
		
	def requestHeartBeat(self):
		with self.socketLock:
			self.socket.sendall(b"requestHeartBeat\0")
			response = str(self.socket.recv(1024).strip(), 'utf-8')
			#print("Gotten HeartBeat response:", response)
			self.lastHeartBeat = time.time()
		if self.running:
				threading.Timer(0.5, self.requestHeartBeat).start()
		
class EMFDeviceInfo(DeviceInfoBase):
	def __init__(self, deviceType, deviceName, deviceAddress, lastHeartBeat, initialEMFState = 0):
		super().__init__(deviceType, deviceName, deviceAddress, lastHeartBeat)
		self.EMFStateRead = initialEMFState
		self.EMFStateWrite = initialEMFState
		self.requestStateInterval = 0.2
		self.publishStateInterval = 0.2
		self.requestStateTimer = threading.Timer(self.requestStateInterval, self.requestState).start()
		self.publishStateTimer = threading.Timer(self.publishStateInterval, self.publishState).start()
		self.selfStateIterTimer = threading.Timer(1.0, self.selfStateIter).start()
		
	def selfStateIter(self):
		if self.running:
			threading.Timer(1.0, self.selfStateIter).start()
		self.EMFStateWrite += 1 
		
	def requestState(self):
		with self.socketLock:
			print(threading.current_thread().getName(), "Aquired lock")
			print(threading.current_thread().getName(), "Sending message: requestState\0")
			self.socket.sendall(b"requestState\0")
			print(threading.current_thread().getName(), "waiting for requestState response...")
			response = str(self.socket.recv(1024).strip(), 'utf-8')
			print(threading.current_thread().getName(), "Gotten requestState response:", response)
			stateValue = int(response.split(":")[1])
			self.EMFStateRead = stateValue
		print(threading.current_thread().getName(), "Released lock")
		if self.running:
			threading.Timer(self.requestStateInterval, self.requestState).start()
			
	def publishState(self):
		with self.socketLock:
			print(threading.current_thread().getName(), "Aquired lock")
			message = str("setClientState:" + str(self.EMFStateWrite) + "\0").encode()
			print(threading.current_thread().getName(), "Sending message: ", message)
			self.socket.sendall(message)
			print(threading.current_thread().getName(), "waiting for setClientState response...")
			response = str(self.socket.recv(1024).strip(), 'utf-8')
			print(threading.current_thread().getName(), "Gotten setClientState response:", response)
		print(threading.current_thread().getName(), "Released lock")
		if self.running:
				threading.Timer(self.publishStateInterval, self.publishState).start()
		
		

class DeviceManager():
	def __init__(self):
		self.deviceList = []
		self.running = True
		self.networkStatusThread = threading.Timer(1.0, self.updateNetworkStatuses).start()
		
	def updateNetworkStatuses(self):
		subprocessResult = subprocess.run(["ip", "neigh", "show", "dev", "wlan0"], capture_output=True)
		stdoutString = subprocessResult.stdout.decode()
		deviceStrings = stdoutString.split("\n")[:-1]
		for deviceString in deviceStrings:
			components = deviceString.split(" ")
			ip = components[0]
			state = components[-1]
			deviceIndex = self.getDeviceIndexByAddress(ip)
			#print("deviceIndex:", deviceIndex)
			if deviceIndex != -1:
				self.deviceList[deviceIndex].connectionStatus = state
			else:
				self.requestDeviceInfo(ip)
		if self.running:
			threading.Timer(1.0, self.updateNetworkStatuses).start()
				
	def requestDeviceInfo(self, ip):
		s = socket.socket()
		port = 80
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((ip, port))
			s.sendall(b"requestClientName\0")
			response = str(s.recv(1024).strip(), 'utf-8')
			messageValues = response.split(":")
			deviceType = messageValues[1]
			deviceName = messageValues[2]
			if deviceType == "EMFReader":
				device = EMFDeviceInfo(deviceType = deviceType, deviceName = deviceName, deviceAddress = ip, lastHeartBeat = 0, initialEMFState = 0)
				dm.registerDevice(device)
			else:
				print("Device type: ", deviceType, "not recognized")
				
	def registerDevice(self, device):
		if device in self.deviceList:
			print("Device", device.deviceName, "already registered")
		else:
			#print("Registering device", device.deviceName)
			self.deviceList.append(device)
	
	def isRegisteredDeviceAddress(self, address):
		for device in self.deviceList:
			if device.deviceAddress[0] == address[0]:
				return True
		return False
	
	def getDeviceIndexByName(self, name):
		for device in self.deviceList:
			if device.deviceName == name:
				return self.deviceList.index(device)
		return -1

	def getDeviceIndexByAddress(self, address):
		localAddressList = []
		for device in self.deviceList:
			localAddressList.append(device.deviceAddress)
			if device.deviceAddress == address:
				return self.deviceList.index(device)
		return -1
	
	def initShutdown(self):
		self.running = False
		for device in self.deviceList:
			device.shutdownDevice()


dm = DeviceManager()

threading.Timer(10.0, dm.initShutdown).start()

while dm.running:
	for i in range(len(dm.deviceList)):
		if dm.deviceList[i].deviceType == "EMFReader":
			1+1
			#sys.stdout.write('\rClient name: %s, EMFStateRead: %d, Connection state: %s' % (dm.deviceList[i].deviceName, dm.deviceList[i].EMFStateRead, dm.deviceList[i].connectionStatus))
#sys.stdout.write('\n')