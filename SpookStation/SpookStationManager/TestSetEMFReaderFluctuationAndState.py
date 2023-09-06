from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType
import time

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

manager = SpookStationManager()

manager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)


inputState = input("Enter desired state: ")
manager.devices["EMFReader1"].setDesiredState(int(inputState))

inputFluctuationRate = input("Enter desired fluctuation rate: ")
manager.devices["EMFReader1").fluctuationRate = (int(inputFluctuationRate))

inputFluctuationMagnitude = input("Enter desired fluctuation magnitude: ")
manager.devices["EMFReader1"].fluctuationMagnitude = (int(inputFluctuationMagnitude))

while 1:
    print(manager.devices["EMFReader1"], end=" ")
    print("Current state: " + str(manager.devices["EMFReader1"].getCurrentState()))
    time.sleep(0.01)
    print(LINE_UP, end=LINE_CLEAR)