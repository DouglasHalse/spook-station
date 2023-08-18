import pyttsx3
import paho.mqtt.client as mqtt
import threading
import numpy as np
import sounddevice as sd
import sys
import sched
import time

class _TTS:
	engine = None
	rate = None
	def __init__(self, volume, rate, voice):
		self.engine = pyttsx3.init()
		self.engine.setProperty('volume', volume)
		self.engine.setProperty('rate', rate)
		self.engine.setProperty('voice', voice)

	def start(self,text_):
		self.engine.say(text_)
		self.engine.runAndWait()

class SpiritBoxMQTTClient():
	def __init__(self, deviceName: str, ipAddress: str = "192.168.7.1", enableDebugPrints: bool = False):
		self.deviceName = deviceName
		self.enableDebugPrints = enableDebugPrints
  
		self.availableVoicesString = str()
		self.engine = pyttsx3.init()
		self.availableVoicesList = self.engine.getProperty('voices')
		for voice in self.availableVoicesList:
			if voice != self.availableVoicesList[-1]:
				self.availableVoicesString += voice.name + ","
			else:
				self.availableVoicesString += voice.name
		del(self.engine)
		self.debugPrint("Available voices: " + self.availableVoicesString)

		self.isTalking = False
		self.lastWordsSaid = str()
		self.volume = 1.0
		self.rate = 300
		self.voice = self.availableVoicesList[0].id
		self.staticVolume = 0.1
		self.staticVolumeWhileTalking = 0.1

		self.outputStream = sd.OutputStream(callback=self.whiteNoiseCallback, channels=1)
		self.outputStream.stop()

		self.SpiritBoxStateTopics = ["/getVolume", "/getRate", "/getVoice", "/availableVoices", "/getStaticVolume", "/getStaticVolumeWhileTalking"]
		self.SpiritBoxControlTopics = ["/setVolume", "/setRate", "/setVoice", "/say", "/setStaticVolume", "/setStaticVolumeWhileTalking"]
		self.MQTTClient = mqtt.Client()
		self.MQTTClient.connect(ipAddress, 1883, 60)
		self.MQTTClient.on_connect = self._on_connect
		self.MQTTClient.on_message = self._on_message
		self.MQTTClient.loop_start()

		self._sendVolume()
		self._sendRate()
		self._sendVoice()
		self._sendStaticVolume()
		self._sendStaticVolumeWhileTalking()
		self._sendAvailableVoices()

	def debugPrint(self, text: str):
		if self.enableDebugPrints:
			print(self.deviceName + ":\t" + text)		

	def voiceIdToName(self, voiceId: str) -> str:
		for voice in self.availableVoicesList:
			if voice.id == voiceId:
				return voice.name
		return ""
		
	def whiteNoiseCallback(self, outdata, frames, time, status): 
		if status:
			print(status, file=sys.stderr)
		if self.isTalking:
			outdata[:] = np.random.rand(frames, 1)*self.staticVolumeWhileTalking*0.1
		else:
			outdata[:] = np.random.rand(frames, 1)*self.staticVolume*0.1
        
	def _on_connect(self, client, userdata, flags, rc):
		self.debugPrint("Connected with result code: " + str(rc))
		self._subscribeToTopics()
		self.outputStream.start()

	def _subscribeToTopics(self):
		for topic in self.SpiritBoxControlTopics:
			fullTopic = self.deviceName + topic
			self.debugPrint("Subscribing to topic: " + fullTopic)
			self.MQTTClient.subscribe(fullTopic)
   
	def _on_message(self, client, userdata, msg):
		if msg.topic == self.deviceName + "/setVolume":
			volume = float(msg.payload)
			self._setVolume(volume)
		elif msg.topic == self.deviceName + "/setRate":
			rate = int(msg.payload)
			self._setRate(rate)
		elif msg.topic == self.deviceName + "/setVoice":
			voice = msg.payload.decode('utf-8')
			self._setVoice(voice)
		elif msg.topic == self.deviceName + "/say":
			self._say(msg.payload.decode('utf-8'))
		elif msg.topic == self.deviceName + "/setStaticVolume":
			volume = float(msg.payload)
			self._setStaticVolume(volume)
		elif msg.topic == self.deviceName + "/setStaticVolumeWhileTalking":
			volume = float(msg.payload)
			self._setStaticVolumeWhileTalking(volume)
		else:
			print("Unknown topic: " + msg.topic)
  
	def _setVolume(self, volume):
		if volume != self.volume:
			self.debugPrint("Volume changed from " + str(self.volume) + " to " + str(volume))
			self.volume = volume
			self._sendVolume()
			return
		self._sendVolume()
	
	def _setRate(self, rate):
		if rate != self.rate:
			self.debugPrint("Rate changed from " + str(self.rate) + " to " + str(rate))
			self.rate = rate
			self._sendRate()
			return
		self._sendRate()

	def _setVoice(self, voiceName):
		if voiceName != self.voiceIdToName(self.voice): 
			for voice in self.availableVoicesList:
				if voice.name == voiceName:
					self.debugPrint("Voice changed from " + self.voiceIdToName(self.voice) + " to " + voice.name)
					self.voice = voice.id
					self._sendVoice()
					return
			print("Unknown voice: " + voiceName)
		self._sendVoice()
    
	def _setStaticVolume(self, volume):
		if self.staticVolume != volume:
			self.debugPrint("Static volume changed from " + str(self.staticVolume) + " to " + str(volume))
			self.staticVolume = volume
			self._sendStaticVolume()
			return
		self._sendStaticVolume()

	def _setStaticVolumeWhileTalking(self, volume):
		if self.staticVolumeWhileTalking != volume:
			self.debugPrint("Static volume while talking changed from " + str(self.staticVolumeWhileTalking) + " to " + str(volume))
			self.staticVolumeWhileTalking = volume
			self._sendStaticVolumeWhileTalking()
			return
		self._sendStaticVolumeWhileTalking()
  
	def _sendVolume(self):
		volume = self.volume
		self.debugPrint("Sending volume: " + str(volume))
		self.MQTTClient.publish(self.deviceName + "/getVolume", volume)

	def _sendStaticVolume(self):
		self.debugPrint("Sending static volume: " + str(self.staticVolume))
		self.MQTTClient.publish(self.deviceName + "/getStaticVolume", self.staticVolume)

	def _sendStaticVolumeWhileTalking(self):
		self.debugPrint("Sending static volume while talking: " + str(self.staticVolumeWhileTalking))
		self.MQTTClient.publish(self.deviceName + "/getStaticVolumeWhileTalking", self.staticVolumeWhileTalking)
  
	def _sendRate(self):
		self.debugPrint("Sending rate: " + str(self.rate))
		self.MQTTClient.publish(self.deviceName + "/getRate", str(self.rate))

	def _sendVoice(self):
		voiceId = self.voice
		for voice in self.availableVoicesList:
			if voice.id == voiceId:
				self.debugPrint("Sending voice: " + voice.name)
				self.MQTTClient.publish(self.deviceName + "/getVoice", voice.name)
				return
		print("voiceId not found in availableVoicesList")
  
	def _sendAvailableVoices(self):
		self.MQTTClient.publish(self.deviceName + "/availableVoices", self.availableVoicesString)

	def _say(self, text):
		self.isTalking = True
		self.debugPrint("Saying: " + text)
		tts = _TTS(volume=self.volume, rate=self.rate, voice=self.voice)
		tts.start(text)
		del(tts)
		self.isTalking = False
		self.lastWordsSaid = text
	