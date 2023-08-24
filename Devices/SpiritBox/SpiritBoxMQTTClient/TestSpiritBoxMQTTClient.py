from SpiritBoxMQTTClient import SpiritBoxMQTTClient
import time


client = SpiritBoxMQTTClient("SpiritBox1")

while 1:
    print("Alive")
    time.sleep(10)