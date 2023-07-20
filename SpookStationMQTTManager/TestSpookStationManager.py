from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType
import time

manager = SpookStationManager()

manager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)

while 1:
	devices = manager.getRegisteredDevices()
	for device in devices:
		if device.deviceType == SpookStationDeviceType.EMFReader:
			print(device, end="\r")

	time.sleep(1)