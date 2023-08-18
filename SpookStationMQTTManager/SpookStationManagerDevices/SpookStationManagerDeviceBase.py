from SpookStationManagerEnums import SpookStationDeviceConnectionState, SpookStationDeviceType
import time

class SpookStationDeviceBase():
	def __init__(self, deviceName: str, deviceType: SpookStationDeviceType, enableDebugPrints: bool = False) -> None:
		self.stateTopics = []
		self.deviceName = deviceName
		self.deviceType = deviceType
		self.lastMessage = 0
		self.enableDebugPrints = enableDebugPrints
		
	def __str__(self) -> str:
		return "Name: " + self.deviceName + " Type: " + str(self.deviceType) + " ConnectionState" + str(self.getConnectionState())
	
	def updateLastMessage(self):
		self.lastMessage = time.time()

	def getConnectionState(self):
		if time.time() - self.lastMessage < 1:
			return SpookStationDeviceConnectionState.Connected
		elif time.time() - self.lastMessage < 5:
			return SpookStationDeviceConnectionState.PoorConnection
		else:
			return SpookStationDeviceConnectionState.Disconnected