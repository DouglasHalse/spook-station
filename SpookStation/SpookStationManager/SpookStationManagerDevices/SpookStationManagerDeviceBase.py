from SpookStationManagerEnums import SpookStationDeviceConnectionState, SpookStationDeviceType
import time, threading

class SpookStationDeviceBase():
	def __init__(self, deviceName: str, deviceType: SpookStationDeviceType, enableDebugPrints: bool = False) -> None:
		self.stateTopics = []
		self.deviceName = deviceName
		self.deviceType = deviceType
		self.lastMessage = 0
		self.enableDebugPrints = enableDebugPrints
		self.lastConnectionState = SpookStationDeviceConnectionState.Disconnected
		self.onConnectionStateChanged = None
		self.repeatConnectionState = True
		self.RepeatingConnectionStateCheck()

	def destroy(self):
		self.repeatConnectionState = False
		
	def __str__(self) -> str:
		return "Name: " + self.deviceName + " Type: " + str(self.deviceType) + " ConnectionState" + str(self.getConnectionState())
	
	def updateLastMessage(self):
		self.lastMessage = time.time()

	def getConnectionState(self):
		if time.time() - self.lastMessage < 1:
			return SpookStationDeviceConnectionState.Connected
		elif time.time() - self.lastMessage < 3:
			return SpookStationDeviceConnectionState.PoorConnection
		else:
			return SpookStationDeviceConnectionState.Disconnected

	def RepeatingConnectionStateCheck(self):
		currentConnectionState = self.getConnectionState()
		if self.lastConnectionState != currentConnectionState and self.onConnectionStateChanged != None:
			print("ConnectionState for " + self.deviceName + " changed to " + str(currentConnectionState))
			self.onConnectionStateChanged(currentConnectionState)
			self.lastConnectionState = currentConnectionState
		if self.repeatConnectionState:
			thread = threading.Timer(0.5, self.RepeatingConnectionStateCheck)
			thread.setName("SpookStationDeviceBaseRepeatingConnectionStateCheck")
			thread.start()

	def setOnConnectionStateChangeCallback(self, callback):
		self.onConnectionStateChanged = callback
