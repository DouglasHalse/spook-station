import paho.mqtt.client as mqtt
import time


class SpookStationManager():
	
	def __init__(self):
		self.EMFDevices = ["EMFReader1"]
		self.EMFTopics = ["desired_state", "current_state"]
		
		self.stateTopics = []
		for EMFDevice in self.EMFDevices:
			self.stateTopics.append(EMFDevice + "/current_state")
		
		
		self.devices = self.EMFDevices
		self.deviceHeartbeats = dict.fromkeys(self.devices, 0)
		self.aliveTimeOut = 1
		
		
		self.client = mqtt.Client(userdata="isSpookStation")
		self.client.on_connect = self.__on_connect
		self.client.on_message = self.__on_message

		self.client.connect_async("localhost", 1883, 60)

		self.client.loop_start()
		
	def __on_connect(self, client, userdata, flags, rc):
		print("Connected with result code: "+str(rc))
		
		self.__subscribeToTopics()
		

		
	def __updateDeviceHeartbeat(self, deviceName):
		if deviceName not in self.deviceHeartbeats.keys():
			print("Device not found in self.deviceHeartbeats: " + deviceName)
			return 0
		self.deviceHeartbeats[deviceName] = time.time()
		
	
	
	def __on_message(self, client, userdata, msg):
		deviceName, deviceTopic = msg.topic.split("/")
		if msg.topic in self.stateTopics:
			self.__updateDeviceHeartbeat(deviceName)
		
		

	def __subscribeToTopics(self):
		for EMFDevice in self.EMFDevices:
			for EMFTopic in self.EMFTopics:
				topicString = EMFDevice + "/" + EMFTopic
				print("Subscribing to topic: " + topicString)
				self.client.subscribe(topicString)
				
	def getAliveDevices(self):
		aliveDict = dict()
		for deviceName in self.devices:
			deviceLastMessage = self.deviceHeartbeats[deviceName]
			isDeviceAlive = deviceLastMessage + self.aliveTimeOut > time.time()
			aliveDict[deviceName] = isDeviceAlive
		return aliveDict
