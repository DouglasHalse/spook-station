from EMFReaderMQTTClientEmulator import EMFReaderMQTTClientEmulator
import time

client = EMFReaderMQTTClientEmulator("EMFReader1", ipAddress="localhost", enableDebugPrints=True)

while 1:
    print("Alive")
    time.sleep(10)