
import paho.mqtt.client as mqtt
import time
from datetime import datetime


def onMessage(client, userdata, msg):
	print(datetime.now())

def on_connect(client, userdata, flags, rc):
	client.subscribe("EMFReader1/current_state")
	print("Connected")


client = mqtt.Client()
client.on_message = onMessage
client.on_connect = on_connect

client.connect_async("localhost", 1883, 60)



client.loop_start()

while 1:
	time.sleep(10)
