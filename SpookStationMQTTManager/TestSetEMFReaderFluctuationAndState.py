from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType
import time

manager = SpookStationManager()

manager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)


inputState = input("Enter desired state: ")
manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].setDesiredState(int(inputState))

inputFluctuationRate = input("Enter desired fluctuation rate: ")
manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].setFluctuationRate(int(inputFluctuationRate))

inputFluctuationMagnitude = input("Enter desired fluctuation magnitude: ")
manager.devices[manager.getDeviceIndex(deviceName="EMFReader1")].setFluctuationMagnitude(int(inputFluctuationMagnitude))

while 1:
    1+1