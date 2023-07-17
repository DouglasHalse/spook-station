import paho.mqtt.client as mqtt
import time

EMFDevices = ["EMFReader1"]

EMFTopics = ["desired_state", "current_state"]


def subscribeToTopics():
	for EMFDevice in EMFDevices:
		for EMFTopic in EMFTopics:
			topicString = EMFDevice + "/" + EMFTopic
			print("Subscribing to topic: " + topicString)
			client.subscribe(topicString)




# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    subscribeToTopics()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect_async("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while 1:
	print("Running")
	time.sleep(10)
