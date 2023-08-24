import sys, os, time
import paho.mqtt.client as mqtt
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStation', 'SpookStationManager'))

from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationDeviceConnectionState

mockGui = mqtt.Client()
mockGui.connect_async("localhost", 1883, 60)
mockGui.loop_start()

deviceManager = SpookStationManager()
deviceManager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)

time.sleep(1)


print("#"*50)
print("Valdiating connection to EMFReader1...")

time.sleep(1)
print("Verifying EMFReader1 connection state = SpookStationDeviceConnectionState.Connected")
emfReaderConnectionState = deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].getConnectionState()
if (emfReaderConnectionState != SpookStationDeviceConnectionState.Connected):
    exit("EMFReader1 has connection state: " + str(emfReaderConnectionState) + " instead of SpookStationDeviceConnectionState.Connected!")

print("Connection to EMFReader1 successful!")
print("#"*50 + "\n")


print("#"*50)
print("Testing state changing for EMFReader1...")

for desiredState in range(0, 5):
    deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].setDesiredState(desiredState)
    time.sleep(1)
    currentState = deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].getCurrentState()
    print("Verifying EMFReader1 desired state = current state")
    if (currentState != desiredState):
        print("EMFReader has state: " + str(currentState) + " instead of " + str(desiredState) + "!")
        exit("State change failed in state changing test!")

print("State change successful!")
print("#"*50 + "\n")

print("#"*50)
print("Testing use sound changing for EMFReader1...")

for desiredUseSound in [True, False]:
    deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].setDesiredUseSound(desiredUseSound)
    time.sleep(1)
    currentUseSound = deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].getCurrentUseSound()
    if (currentUseSound != desiredUseSound):
        print("EMFReader has use sound: " + str(currentUseSound) + " instead of " + str(desiredUseSound) + "!")
        exit("Use sound change failed!")
    time.sleep(1)

print("Use sound change successful!")
print("#"*50 + "\n")


print("#"*50)
print("Testing state fluctuation magnitude for EMFReader1...")

desiredState = 2
#ensure that fluctuation will happen
deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].setFluctuationRate(1)
deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].setDesiredState(desiredState)
time.sleep(1)
currentState = deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].getCurrentState()
if (currentState != 2):
    print("EMFReader has state: " + str(currentState) + " instead of " + str(desiredState) + "!")
    exit("State change failed in state fluctuation magnitude test!")
time.sleep(1)
for fluctuationMagnitude in range(0, 3):
    deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].setFluctuationMagnitude(fluctuationMagnitude)
    time.sleep(1)
    for i in range(0, 100):
        currentState = deviceManager.devices[deviceManager.getDeviceIndex("EMFReader1")].getCurrentState()
        if currentState < desiredState - fluctuationMagnitude or currentState > desiredState + fluctuationMagnitude:
            print("EMFReader has state: " + str(currentState) + " which is outside of the fluctuation magnitude of " + str(desiredState) + "+-" + str(fluctuationMagnitude) + "!")
            exit("Fluctuation magnitude change failed!")
        time.sleep(0.01)

print("Fluctuation magnitude change successful!")
print("#"*50 + "\n")

print("All tests successful!")

del deviceManager, mockGui

sys.exit()