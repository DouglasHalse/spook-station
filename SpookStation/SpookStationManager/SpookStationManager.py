import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationSignalType, SpookStationDeviceConnectionState
from SpookStationManagerDevices.SpookStationManagerDeviceEMFReader import SpookStationManagerDeviceEMFReader
from SpookStationManagerDevices.SpookStationManagerDeviceSpiritbox import SpookStationManagerDeviceSpiritbox
from SpookStationManagerDevices.SpookStationManagerDeviceUtil import SpookStationSignal
import time
import threading


class SpookStationManager():
	def __init__(self, useCyclicControlSignalPublishing: bool = True, enableDebugPrints = False) -> None:
		self.enableDebugPrints = enableDebugPrints
		self.devices = dict()
		self.useCyclicControlSignalPublishing = useCyclicControlSignalPublishing
		self.shuttingDown = False

		self.client = mqtt.Client(userdata="isSpookStation")
		self.client.on_message = self.__on_message
		self.client.on_connect = self._on_connect
		self.client.connect_async("localhost", 1883, 60)

		self.bytesReceivedTopic = "$SYS/broker/load/bytes/received/1min"
		self.bytesReceivedCallback = None
		self.bytesReceivedCurrent = None

		self.bytesSentTopic = "$SYS/broker/load/bytes/sent/1min"
		self.bytesSentCallback = None
		self.bytesSentCurrent = None

		self.systemTopics = [self.bytesReceivedTopic, self.bytesSentTopic]

		self.client.loop_start()

	def destroy(self):
		print("SpookStationManager destructor called")
		self.shuttingDown = True
		self.useCyclicControlSignalPublishing = False
		self.client.loop_stop()
		self.client.disconnect()
		for device in self.devices.values():
			device.destroy()
		del self.client
	
	def debugPrint(self, text: str):
		if self.enableDebugPrints:
			print("SpookStation:\t" + text)	

	def cyclicControlSignalPublishing(self):
		self.publishControlTopics()
		if self.useCyclicControlSignalPublishing:
			thread = threading.Timer(0.1, self.cyclicControlSignalPublishing)
			thread.setName("SpookStationManagerCyclicControlSignalPublishing")
			thread.start()

	def cyclicBytesReceived(self):
		if self.bytesReceivedCallback is not None:
			self.bytesReceivedCallback(self.bytesReceivedCurrent)
		if not self.shuttingDown:
			thread = threading.Timer(1, self.cyclicBytesReceived)
			thread.setName("SpookStationManagerCyclicBytesReceived")
			thread.start()

	def cyclicBytesSent(self):
		if self.bytesSentCallback is not None:
			self.bytesSentCallback(self.bytesSentCurrent)
		if not self.shuttingDown:
			thread = threading.Timer(1, self.cyclicBytesSent)
			thread.setName("SpookStationManagerCyclicBytesSent")
			thread.start()

	def _on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.debugPrint("Connected to broker")
			for topic in self.systemTopics:
				self.debugPrint("Subscribing to: " + topic)
				self.client.subscribe(topic, options=SubscribeOptions(qos=2))
			self.cyclicBytesSent()
			self.cyclicBytesReceived()
			if self.useCyclicControlSignalPublishing:
				self.cyclicControlSignalPublishing()
		else:
			self.debugPrint("Failed to connect to broker, return code: " + str(rc))

	def __on_message(self, client, userdata, msg):

		if self.bytesReceivedTopic == msg.topic:
			bytesPerSeconds = round(float(msg.payload.decode("utf-8"))/60, 2)
			self.debugPrint("Broker bytes received: " + str(bytesPerSeconds) + " B/s")
			self.bytesReceivedCurrent = bytesPerSeconds
			return

		if self.bytesSentTopic == msg.topic:
			bytesPerSeconds = round(float(msg.payload.decode("utf-8"))/60, 2)
			self.debugPrint("Broker bytes sent: " + str(bytesPerSeconds) + " B/s")
			self.bytesSentCurrent = bytesPerSeconds
			return

		deviceName, deviceTopic = msg.topic.split("/")

		assert deviceName in self.devices.keys(), "Received message for unknown device: " + deviceName

		device = self.devices[deviceName]

		if device.deviceType == SpookStationDeviceType.EMFReader:
			if deviceTopic == "current_state":
				device.setCurrentState(int(msg.payload.decode("utf-8")))
			elif deviceTopic == "current_use_sound":
				currentUseSoundString = msg.payload.decode("utf-8")
				if currentUseSoundString == "True" or currentUseSoundString == "true":
					device.useSound.setValue(True, signalType=SpookStationSignalType.State)
				else:
					device.useSound.setValue(False, signalType=SpookStationSignalType.State)
			device.updateLastMessage()
			return
		elif device.deviceType == SpookStationDeviceType.SpiritBox:
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
		self.client.loop_stop()
		for topic in device.stateTopics:
			self.debugPrint("Subscribing to: " + topic)
			self.client.subscribe(topic, options=SubscribeOptions(qos=2))
		self.client.loop_start()


	def __unSubscribeToTopics(self, device):
		for topic in device.stateTopics:
			self.debugPrint("Unsubscribing to: " + topic)
			self.client.unsubscribe(topic)

	def __getDeviceTypeFromName(self, deviceName: str):
		assert deviceName in self.devices.keys(), "Unknown device: " + deviceName
		return self.devices[deviceName].deviceType
	
	def publishControlTopics(self):
		for device in self.devices.values():
			if device.deviceType == SpookStationDeviceType.EMFReader:
				# Publish EMFReader state
				stateWithFluctuation = device.getDesiredStateWithFluctuation()
				self.client.publish(device.state.controlTopic, stateWithFluctuation, qos=2)
				self.debugPrint("Publishing desired state: " + str(stateWithFluctuation) + " for " + device.deviceName)
				
				# Publish EMFReader useSound
				if device.useSound.hasChanged(signalType=SpookStationSignalType.Control):
					desiredUseSoundString = "true" if device.useSound.getValue(signalType=SpookStationSignalType.Control) else "false"
					self.client.publish(device.useSound.controlTopic, desiredUseSoundString, qos=2)
					device.useSound.resetHasChanged(signalType=SpookStationSignalType.Control)
					self.debugPrint("Publishing desired use sound: " + desiredUseSoundString + " for " + device.deviceName)

			elif device.deviceType == SpookStationDeviceType.SpiritBox:
				# Publish SpiritBox speechVolume
				if device.speechVolume.hasChanged(signalType=SpookStationSignalType.Control):
					self.client.publish(device.speechVolume.controlTopic, device.speechVolume.getValue(SpookStationSignalType.Control), qos=2)
					device.speechVolume.resetHasChanged(signalType=SpookStationSignalType.Control)
					self.debugPrint("Publishing desired speech volume: " + str(device.speechVolume.getValue(SpookStationSignalType.Control)) + " for " + device.deviceName)

				# Publish SpiritBox speechRate
				if device.speechRate.hasChanged(signalType=SpookStationSignalType.Control):
					self.client.publish(device.speechRate.controlTopic, device.speechRate.getValue(SpookStationSignalType.Control), qos=2)
					device.speechRate.resetHasChanged(signalType=SpookStationSignalType.Control)
					self.debugPrint("Publishing desired speech rate: " + str(device.speechRate.getValue(SpookStationSignalType.Control)) + " for " + device.deviceName)

				# Publish SpiritBox voice
				if device.voice.hasChanged(signalType=SpookStationSignalType.Control):
					self.client.publish(device.voice.controlTopic, device.voice.getValue(SpookStationSignalType.Control), qos=2)
					device.voice.resetHasChanged(signalType=SpookStationSignalType.Control)
					self.debugPrint("Publishing desired voice: " + str(device.voice.getValue(SpookStationSignalType.Control)) + " for " + device.deviceName)

				# Publish SpiritBox staticVolume
				if device.staticVolume.hasChanged(signalType=SpookStationSignalType.Control):
					self.client.publish(device.staticVolume.controlTopic, device.staticVolume.getValue(SpookStationSignalType.Control), qos=2)
					device.staticVolume.resetHasChanged(signalType=SpookStationSignalType.Control)
					self.debugPrint("Publishing desired static volume: " + str(device.staticVolume.getValue(SpookStationSignalType.Control)) + " for " + device.deviceName)

				# Publish SpiritBox staticVolumeWhileTalking
				if device.staticVolumeWhileTalking.hasChanged(signalType=SpookStationSignalType.Control):
					self.client.publish(device.staticVolumeWhileTalking.controlTopic, device.staticVolumeWhileTalking.getValue(SpookStationSignalType.Control), qos=2)
					device.staticVolumeWhileTalking.resetHasChanged(signalType=SpookStationSignalType.Control)
					self.debugPrint("Publishing desired static volume while talking: " + str(device.staticVolumeWhileTalking.getValue(SpookStationSignalType.Control)) + " for " + device.deviceName)

				# Publish SpiritBox wordsToSay
				if device.hasWordsToSay():
					self.client.publish(device.wordsToSay.controlTopic, device.wordsToSay.getValue(SpookStationSignalType.Control), qos=2)
					device.wordsToSay.resetHasChanged(signalType=SpookStationSignalType.Control)
					device.wordsToSay.resetSignal()
					self.debugPrint("Publishing desired words to say: " + str(device.wordsToSay.getValue(SpookStationSignalType.Control)) + " for " + device.deviceName)

			else:
				print("Unknown device type for publishing control signals: " + str(device.deviceType))
				
	def getAliveDevices(self) -> list:
		aliveDevices = []
		for device in self.devices.values():
			if device.getConnectionState() == SpookStationDeviceConnectionState.Connected:
				aliveDevices.append(device)
		return aliveDevices

	def addDevice(self, deviceName: str, deviceType: SpookStationDeviceType):
		assert deviceName not in self.devices.keys(), "Device already registered: " + deviceName
		if deviceType == SpookStationDeviceType.EMFReader:
			device = SpookStationManagerDeviceEMFReader(deviceName)
		elif deviceType == SpookStationDeviceType.SpiritBox:
			device = SpookStationManagerDeviceSpiritbox(deviceName)
		self.devices[deviceName] = device
		self.__subscribeToTopics(device)
	
	def removeDevice(self, deviceName: str):
		assert deviceName in self.devices.keys(), "Device not registered: " + deviceName
		self.__unSubscribeToTopics(self.devices[deviceName])
		self.devices[deviceName].destroy()
		del self.devices[deviceName]

	def getRegisteredDevices(self):
		return self.devices.values()