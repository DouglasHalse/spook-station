import paho.mqtt.client as mqtt
import threading

class EMFReaderMQTTClientEmulator():
	def __init__(self, deviceName: str, ipAddress: str = "192.168.7.1", enableDebugPrints: bool = False):
		self.deviceName = deviceName
		self.enableDebugPrints = enableDebugPrints

		self.currentState = 0
		self.currentUseSound = False

		self.currentStateTopic = self.deviceName + "/current_state"
		self.currentUseSoundTopic = self.deviceName + "/current_use_sound"
		self.EMFReaderStateTopics = [self.currentStateTopic, self.currentUseSoundTopic]

		self.desiredStateTopic = self.deviceName + "/desired_state"
		self.desiredUseSoundTopic = self.deviceName + "/desired_use_sound"
		self.EMFReaderControlTopics = [self.desiredStateTopic, self.desiredUseSoundTopic]
		
		self.MQTTClient = mqtt.Client()
		self.MQTTClient.connect(ipAddress, 1883, 60)
		self.MQTTClient.on_connect = self._on_connect
		self.MQTTClient.on_message = self._on_message
		self.MQTTClient.loop_start()

	def debugPrint(self, text: str):
		if self.enableDebugPrints:
			print(self.deviceName + ":\t" + text)	

	def _on_connect(self, client, userdata, flags, rc):
		self.debugPrint("Connected with result code " + str(rc))
		for topic in self.EMFReaderControlTopics:
			self.MQTTClient.subscribe(topic)
		self.cyclicStatePublishing()

	def _on_message(self, client, userdata, msg):
		if msg.topic == self.desiredStateTopic:
			self.debugPrint("Setting current state to " + str(msg.payload.decode()))
			self.currentState = int(msg.payload)
		elif msg.topic == self.desiredUseSoundTopic:
			self.debugPrint("Setting current use sound to " + str(msg.payload.decode()))
			useSoundString = msg.payload.decode()
			if useSoundString == "True" or useSoundString == "true":
				self.currentUseSound = True
			else:
				self.currentUseSound = False

	def cyclicStatePublishing(self):
		self.MQTTClient.publish(self.currentStateTopic, self.currentState)
		self.MQTTClient.publish(self.currentUseSoundTopic, self.currentUseSound)
		threading.Timer(0.05, self.cyclicStatePublishing).start()
