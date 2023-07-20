from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType
import time

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

manager = SpookStationManager()

manager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)


inputState = input("Enter desired state: ")
manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].setDesiredState(int(inputState))

inputFluctuationRate = input("Enter desired fluctuation rate: ")
manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].setFluctuationRate(int(inputFluctuationRate))

inputFluctuationMagnitude = input("Enter desired fluctuation magnitude: ")
manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].setFluctuationMagnitude(int(inputFluctuationMagnitude))

while 1:
    print(manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")], end=" ")
    print("Current state: " + str(manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].getCurrentState()))
    time.sleep(0.01)
    print(LINE_UP, end=LINE_CLEAR)