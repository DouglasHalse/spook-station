from SpookStationManager import SpookStationManager
import time

manager = SpookStationManager()

while 1:
	print(manager.getAliveDevices())
	time.sleep(10)