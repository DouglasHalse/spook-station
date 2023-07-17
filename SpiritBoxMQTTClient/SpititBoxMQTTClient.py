import pyttsx3
import paho.mqtt.client as mqtt


class SpiritBoxMQTTClient():
	
	


engine = pyttsx3.init('espeak')

rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 100)     # setting up new voice rate

volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

voices = engine.getProperty('voices')       #getting details of current voice
#print(voices[0])
print(len(voices))

for i in range(len(voices)):
	print(i)
	print(voices[i])
	
	
engine.setProperty('voice', voices[0].id)   #changing index, changes voices. 1 for female
engine.say("Voice number " +  str(i))
print("Voice number " +  str(i))
engine.runAndWait()

engine.setProperty('voice', voices[65].id)   #changing index, changes voices. 1 for female

engine.say("Släpp  ut mig!")
engine.runAndWait()
