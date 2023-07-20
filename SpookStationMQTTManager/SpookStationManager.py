import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
from SpookStationManagerEnums import SpookStationDeviceType
from SpookStationManagerDevices.SpookStationManagerDeviceEMFReader import SpookStationManagerDeviceEMFReader
import time




class MQTTTopics():
	@staticmethod
	def getStateTopics(deviceType: SpookStationDeviceType):
		if deviceType == SpookStationDeviceType.EMFReader:
			return ["desired_state", "current_state"]
		else:
			return None





class SpookStationManager():
	def __init__(self):
		self.devices = []

		self.aliveTimeOut = 1

		self.client = mqtt.Client(userdata="isSpookStation")
		self.client.on_connect = self.__on_connect
		self.client.on_message = self.__on_message

		self.client.connect_async("localhost", 1883, 60)

		self.client.loop_start()
		
	def __on_connect(self, client, userdata, flags, rc):
		print("Connected with result code: "+str(rc))
	
	def __on_message(self, client, userdata, msg):
		deviceName, deviceTopic = msg.topic.split("/")

		for device in self.devices:
			if device.deviceName == deviceName and device.deviceType == SpookStationDeviceType.EMFReader:
				if deviceTopic == "desired_state":
					device.desiredState = int(msg.payload)
				elif deviceTopic == "current_state":
					device.currentState = int(msg.payload)
				device.updateLastMessage()
				return
			else:
				print("Message for unknown device: " + deviceName)

	def __subscribeToTopics(self, deviceName: str, deviceType: SpookStationDeviceType):
		self.stateTopics = MQTTTopics.getStateTopics(deviceType)
		for topic in self.stateTopics:
			print("Subscribing to: " + deviceName + "/" + topic)
			self.client.loop_stop()
			self.client.subscribe(deviceName + "/" + topic, options=SubscribeOptions(qos=2))
			self.client.loop_start()


	def __unSubscribeToTopics(self, deviceName: str, deviceType: SpookStationDeviceType):
		self.stateTopics = MQTTTopics.getStateTopics(deviceType)
		for topic in self.stateTopics:
			self.client.unsubscribe(deviceName + "/" + topic)

	def __getDeviceTypeFromName(self, deviceName: str):
		for device in self.devices:
			if device.deviceName == deviceName:
				return device.deviceType
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
		self.__subscribeToTopics(deviceName, deviceType)
		return True
	
	def removeDevice(self, deviceName: str):
		for device in self.devices:
			if device.deviceName == deviceName:
				self.devices.remove(device)
				self.__unSubscribeToTopics(deviceName, device.deviceType)
				return True
		return False

	def getRegisteredDevices(self):
		return self.devices