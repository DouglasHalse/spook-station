import pyttsx3
import paho.mqtt.client as mqtt
import threading
import numpy as np
import sounddevice as sd
import sys
import sched
import time

class SpiritBoxMQTTClient():
	def __init__(self, deviceName: str):
		self.deviceName = deviceName
		self.engine = pyttsx3.init('espeak')

		self.outputStream = sd.OutputStream(callback=self.whiteNoiseCallback, channels=1)
		self.outputStream.stop()
		self.isTalking = False
		self.staticVolume = 1.0
		self.staticVolumeWhileTalking = 0.1

		self.MQTTClient = mqtt.Client()
		self.MQTTClient.connect("192.168.7.1", 1883, 60)
		self.MQTTClient.on_connect = self.__on_connect
		self.MQTTClient.on_message = self.__on_message
  
		self.SpiritBoxStateTopics = ["/getVolume", "/getRate", "/getVoice", "/availableVoices", "/getStaticVolume", "/getStaticVolumeWhileTalking"]
		self.SpiritBoxControlTopics = ["/setVolume", "/setRate", "/setVoice", "/say", "/setStaticVolume", "/setStaticVolumeWhileTalking"]

		self.MQTTClient.loop_start()
  
		self.availableVoices = str()
		voices = self.engine.getProperty('voices')
		for voice in voices:
			if voice != voices[-1]:
				self.availableVoices += voice.name + ","
			else:
				self.availableVoices += voice.name

		print("Available voices:" + self.availableVoices)

		self.__repeatSendingVolume()
		self.__repeatSendingRate()
		self.__repeatSendingAvailableVoices()
		self.__repeatSendingVoice()

		
		self.engine.stop()
		self.engine.setProperty('voice', 'swedish')
		self.engine.runAndWait()

		print("Using voice " + self.engine.getProperty('voice'))

		
		
	def whiteNoiseCallback(self, outdata, frames, time, status): 
		if status:
			print(status, file=sys.stderr)
		if self.isTalking:
			outdata[:] = np.random.rand(frames, 1)*self.staticVolumeWhileTalking
		else:
			outdata[:] = np.random.rand(frames, 1)*self.staticVolume


        
	def __on_connect(self, client, userdata, flags, rc):
		print("Connected with result code: " + str(rc) + "\n")
		self.__subscribeToTopics()
		self.outputStream.start()
		
  
	def __subscribeToTopics(self):
		for topic in self.SpiritBoxControlTopics:
			fullTopic = self.deviceName + topic
			print("Subscribing to topic: " + fullTopic)
			self.MQTTClient.subscribe(fullTopic)
   
	def __on_message(self, client, userdata, msg):
		print("Message received on topic: " + msg.topic)
		if msg.topic == self.deviceName + "/setVolume":
			volume = float(msg.payload)
			self.__setVolume(volume)
		elif msg.topic == self.deviceName + "/setRate":
			rate = int(msg.payload)
			self.__setRate(rate)
		elif msg.topic == self.deviceName + "/setVoice":
			voice = msg.payload.decode('utf-8')
			self.__setVoice(voice)
		elif msg.topic == self.deviceName + "/say":
			self.__say(msg.payload)
		elif msg.topic == self.deviceName + "/setStaticVolume":
			volume = float(msg.payload)
			self.__setStaticVolume(volume)
		elif msg.topic == self.deviceName + "/setStaticVolumeWhileTalking":
			volume = float(msg.payload)
			self.__setStaticVolumeWhileTalking(volume)
		else:
			print("Unknown topic: " + msg.topic)
  
	def __repeatSendingVolume(self):
		self.__sendVolume()
		threading.Timer(1, self.__repeatSendingVolume).start()
  
	def __repeatSendingRate(self):
		self.__sendRate()
		threading.Timer(1, self.__repeatSendingRate).start()
  
	def __repeatSendingAvailableVoices(self):
		self.__sendAvailableVoices()
		threading.Timer(1, self.__repeatSendingAvailableVoices).start()

	def __repeatSendingVoice(self):
		self.__sendVoice()
		threading.Timer(1, self.__repeatSendingVoice).start()

	def __repeatSendingStaticVolume(self):
		self.__sendStaticVolume()
		threading.Timer(1, self.__repeatSendingStaticVolume).start()

	def __repeatSendingStaticVolumeWhileTalking(self):
		self.__sendStaticVolumeWhileTalking()
		threading.Timer(1, self.__repeatSendingStaticVolumeWhileTalking).start()
  
	def __setVolume(self, volume):
		print("Setting volume to: " + str(volume) + "\n")
		self.engine.stop()
		self.engine.setProperty('volume', volume)
		self.engine.runAndWait()
		self.__sendVolume()
  
	def __sendVolume(self):
		#print("Sending current volume: " + str(self.engine.getProperty('volume')))
		volume = self.engine.getProperty('volume')
		self.MQTTClient.publish(self.deviceName + "/getVolume", volume)

	def __sendStaticVolume(self):
		self.MQTTClient.publish(self.deviceName + "/getStaticVolume", self.staticVolume)

	def __sendStaticVolumeWhileTalking(self):
		self.MQTTClient.publish(self.deviceName + "/getStaticVolumeWhileTalking", self.staticVolumeWhileTalking)
  
	def __sendRate(self):
		#print("Sending current rate: " + str(self.engine.getProperty('rate')))
		rate = self.engine.getProperty('rate')
		self.MQTTClient.publish(self.deviceName + "/getRate", rate)
  
	def __setRate(self, rate):
		print("Setting rate to: " + str(rate) + "\n")
		self.engine.stop()
		self.engine.setProperty('rate',  rate)
		self.engine.runAndWait()
		self.__sendRate()

	def __setVoice(self, voice):
		if voice in self.availableVoices:
			print("Setting voice to: " + voice)
			self.engine.stop()
			self.engine.setProperty('voice', voice)
			self.engine.runAndWait()
		else:
			print("Unknown voice: " + voice)
    
	def __setStaticVolume(self, volume):
		print("Setting static volume to : " + str(volume))
		self.staticVolume = volume

	def __setStaticVolumeWhileTalking(self, volume):
		print("Setting static volume while talking to : " + str(volume))
		self.staticVolumeWhileTalking = volume

	def __sendVoice(self):
		#print("Sending current voice: " + self.engine.getProperty('voice'))
		voice = self.engine.getProperty('voice')
		self.MQTTClient.publish(self.deviceName + "/getVoice", voice)
  
	def __sendAvailableVoices(self):
		#print("Sending available voices: " + str(self.availableVoices))
		self.MQTTClient.publish(self.deviceName + "/availableVoices", self.availableVoices)

	def __say(self, text):
		self.isTalking = True
		print("Saying: " + text.decode('utf-8'))
		self.engine.say(text.decode('utf-8'))
		self.engine.runAndWait()
		self.isTalking = False
	
