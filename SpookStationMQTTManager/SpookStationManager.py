import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationSignalType
from SpookStationManagerDevices.SpookStationManagerDeviceEMFReader import SpookStationManagerDeviceEMFReader
from SpookStationManagerDevices.SpookStationManagerDeviceSpiritbox import SpookStationManagerDeviceSpiritbox
from SpookStationManagerDevices.SpookStationManagerDeviceUtil import SpookStationSignal
import time
import threading


class SpookStationManager():
	def __init__(self, useCyclicControlSignalPublishing: bool = True, enableDebugPrints = False) -> None:
		self.enableDebugPrints = enableDebugPrints
		self.devices = []
		self.useCyclicControlSignalPublishing = useCyclicControlSignalPublishing

		self.client = mqtt.Client(userdata="isSpookStation")
		self.client.on_message = self.__on_message

		self.client.connect_async("localhost", 1883, 60)

		self.client.loop_start()

		if self.useCyclicControlSignalPublishing:
			self.cyclicControlSignalPublishing()

	def destroy(self):
		print("SpookStationManager destructor called")
		self.useCyclicControlSignalPublishing = False
		self.client.loop_stop()
		self.client.disconnect()
		for device in self.devices:
			device.destroy()
		del self.client
	
	def debugPrint(self, text: str):
		if self.enableDebugPrints:
			print("SpookStation:\t" + text)	

	def publishSpookStationSignal(self, signal: SpookStationSignal, signalType: SpookStationSignalType = SpookStationSignalType.Control):
		if signal.hasChanged(signalType):
			self.debugPrint("Publishing " + signal.name + " with value " + str(signal.getValue(signalType=signalType)) + " for " + signal.deviceName)
			self.client.publish(signal.getTopic(signalType=signalType), str(signal.getValue(signalType=signalType)), qos=2)
			signal.resetHasChanged(signalType=signalType)

	def cyclicControlSignalPublishing(self):
		self.publishControlTopics()
		if self.useCyclicControlSignalPublishing:
			thread = threading.Timer(0.1, self.cyclicControlSignalPublishing)
			thread.setName("SpookStationManagerCyclicControlSignalPublishing")
			thread.start()

	def __on_message(self, client, userdata, msg):
		deviceName, deviceTopic = msg.topic.split("/")

		for device in self.devices:
			if device.deviceName == deviceName and device.deviceType == SpookStationDeviceType.EMFReader:
				if deviceTopic == "current_state":
					device.setCurrentState(int(msg.payload))
				elif deviceTopic == "current_use_sound":
					currentUseSoundString = msg.payload.decode("utf-8")
					if currentUseSoundString == "True" or currentUseSoundString == "true":
						device.setCurrentUseSound(True)
					else:
						device.setCurrentUseSound(False)
				device.updateLastMessage()
				return
			elif device.deviceName == deviceName and device.deviceType == SpookStationDeviceType.SpiritBox:
				if deviceTopic == "getVolume":
					self.debugPrint("Received volume: " + str(msg.payload.decode('utf-8')) + " from " + deviceName)
					device.speechVolume.setValue(float(msg.payload), signalType=SpookStationSignalType.State)
				elif deviceTopic == "getRate":
					self.debugPrint("Received rate: " + str(msg.payload.decode('utf-8')) + " from " + deviceName)
					device.speechRate.setValue(int(msg.payload), signalType=SpookStationSignalType.State)
				elif deviceTopic == "getVoice":
					self.debugPrint("Received voice: " + str(msg.payload.decode('utf-8')) + " from " + deviceName)
					device.voice.setValue(msg.payload.decode('utf-8'), signalType=SpookStationSignalType.State)
				elif deviceTopic == "availableVoices":
					self.debugPrint("Received available voices: " + str(msg.payload.decode('utf-8')) + " from " + deviceName)
					device.availableVoices.setValue(msg.payload.decode('utf-8'), signalType=SpookStationSignalType.State)
				elif deviceTopic == "getStaticVolume":
					self.debugPrint("Received static volume: " + str(msg.payload.decode('utf-8')) + " from " + deviceName)
					device.staticVolume.setValue(float(msg.payload), signalType=SpookStationSignalType.State)
				elif deviceTopic == "getStaticVolumeWhileTalking":
					self.debugPrint("Received static volume while talking: " + str(msg.payload.decode('utf-8')) + " from " + deviceName)
					device.staticVolumeWhileTalking.setValue(float(msg.payload), signalType=SpookStationSignalType.State)
				else:
					print("Unknown topic in message: " + msg.topic)
				device.updateLastMessage()
				return
			else:
				print("Message for unknown device: " + deviceName)

	def __subscribeToTopics(self, device):
		for topic in device.stateTopics:
			self.debugPrint("Subscribing to: " + topic)
			self.client.loop_stop()
			self.client.subscribe(topic, options=SubscribeOptions(qos=2))
			self.client.loop_start()


	def __unSubscribeToTopics(self, device):
		for topic in device.stateTopics:
			self.client.unsubscribe(topic)

	def __getDeviceTypeFromName(self, deviceName: str):
		for device in self.devices:
			if device.deviceName == deviceName:
				return device.deviceType
		return None
	
	def publishControlTopics(self):
		for device in self.devices:
			if device.deviceType == SpookStationDeviceType.EMFReader:
				self.client.publish(device.deviceName + "/desired_state", device.getDesiredState(), qos=2)
				desiredUseSoundString = None
				if(device.getDesiredUseSound()):
					desiredUseSoundString = "true"
				else:
					desiredUseSoundString = "false"
				self.client.publish(device.deviceName + "/desired_use_sound", desiredUseSoundString, qos=2)
			elif device.deviceType == SpookStationDeviceType.SpiritBox:
				self.publishSpookStationSignal(device.speechVolume)
				self.publishSpookStationSignal(device.speechRate)
				self.publishSpookStationSignal(device.voice)
				self.publishSpookStationSignal(device.staticVolume)
				self.publishSpookStationSignal(device.staticVolumeWhileTalking)
				if device.hasWordsToSay():
					self.publishSpookStationSignal(device.wordsToSay)
					# Reset since signal is only for one time use
					device.wordsToSay.resetSignal()

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
		elif deviceType == SpookStationDeviceType.SpiritBox:
			device = SpookStationManagerDeviceSpiritbox(deviceName)
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