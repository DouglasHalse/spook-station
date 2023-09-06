from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType
import time

manager = SpookStationManager()

manager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)

while 1:
    inputState = input("Enter desired state: ")
    manager.devices["EMFReader1"].setDesiredState(int(inputState))
    time.sleep(1)
    currentState = manager.devices["EMFReader1"].getCurrentState()
    print("Current state: " + str(currentState))