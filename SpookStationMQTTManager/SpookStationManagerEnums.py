from enum import Enum

class SpookStationDeviceType(Enum):
    EMFReader = 1
    SpiritBox = 2
    
class SpookStationDeviceConnectionState(Enum):
	Connected = 1
	PoorConnection = 2
	Disconnected = 3