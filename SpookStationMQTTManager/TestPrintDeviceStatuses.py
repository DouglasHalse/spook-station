from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType
import time

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

manager = SpookStationManager()

manager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)

while 1:
	devices = manager.getRegisteredDevices()
	for device in devices:
		if device.deviceType == SpookStationDeviceType.EMFReader:
			print(device)

	time.sleep(1)
	print(LINE_UP, end=LINE_CLEAR)