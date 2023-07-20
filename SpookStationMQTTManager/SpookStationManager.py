import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
from SpookStationManagerEnums import SpookStationDeviceType
from SpookStationManagerDevices.SpookStationManagerDeviceEMFReader import SpookStationManagerDeviceEMFReader
import time
import threading


class SpookStationManager():
	def __init__(self, useCyclicControlSignalPublishing: bool = True) -> None:
		self.devices = []
		self.useCyclicControlSignalPublishing = useCyclicControlSignalPublishing

		self.client = mqtt.Client(userdata="isSpookStation")
		self.client.on_connect = self.__on_connect
		self.client.on_message = self.__on_message

		self.client.connect_async("localhost", 1883, 60)

		self.client.loop_start()

		if self.useCyclicControlSignalPublishing:
			self.cyclicControlSignalPublishing()


	def cyclicControlSignalPublishing(self):
		self.publishControlTopics()
		if self.useCyclicControlSignalPublishing:
			threading.Timer(0.1, self.cyclicControlSignalPublishing).start()


		
	def __on_connect(self, client, userdata, flags, rc):
		#print("Connected with result code: "+str(rc))
		1+1
	
	def __on_message(self, client, userdata, msg):
		deviceName, deviceTopic = msg.topic.split("/")

		for device in self.devices:
			if device.deviceName == deviceName and device.deviceType == SpookStationDeviceType.EMFReader:
				if deviceTopic == "current_state":
					device.setCurrentState(int(msg.payload))
				elif deviceTopic == "current_use_sound":
					device.setCurrentUseSound(bool(msg.payload))
				device.updateLastMessage()
				return
			else:
				print("Message for unknown device: " + deviceName)

	def __subscribeToTopics(self, device):
		for topic in device.stateTopics:
			print("Subscribing to: " + device.deviceName + "/" + topic)
			self.client.loop_stop()
			self.client.subscribe(device.deviceName + "/" + topic, options=SubscribeOptions(qos=2))
			self.client.loop_start()


	def __unSubscribeToTopics(self, device):
		for topic in device.stateTopics:
			self.client.unsubscribe(device.deviceName + "/" + topic)

	def __getDeviceTypeFromName(self, deviceName: str):
		for device in self.devices:
			if device.deviceName == deviceName:
				return device.deviceType
		return None
	
	def publishControlTopics(self):
		for device in self.devices:
			if device.deviceType == SpookStationDeviceType.EMFReader:
				self.client.publish(device.deviceName + "/desired_state", device.desiredState, qos=2)
				self.client.publish(device.deviceName + "/desired_use_sound", device.desiredUseSound, qos=2)
			else:
				print("Unknown device type for publishing control signals: " + str(device.deviceType))

	def getDeviceIndex(self, deviceName: str):
		for index, device in enumerate(self.devices):
			if device.deviceName == deviceName:
				return index
		return None
				
	def getAliveDevices(self) -> list:
		aliveDevices = []
		for device in self.devices:
			if time.time() - device.lastMessage < self.aliveTimeOut:
				aliveDevices.append(device)
		return aliveDevices

	def addDevice(self, deviceName: str, deviceType: SpookStationDeviceType):
		for device in self.devices:
			if device.deviceName == deviceName:
				return False
		if deviceType == SpookStationDeviceType.EMFReader:
			device = SpookStationManagerDeviceEMFReader(deviceName)
		self.devices.append(device)
		self.__subscribeToTopics(device)
		return True
	
	def removeDevice(self, deviceName: str):
		for device in self.devices:
			if device.deviceName == deviceName:
				self.__unSubscribeToTopics(device)
				self.devices.remove(device)
				return True
		return False

	def getRegisteredDevices(self):
		return self.devices