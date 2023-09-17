from enum import Enum

class SpookStationDeviceType(Enum):
    EMFReader = 1
    SpiritBox = 2


SpookStationDeviceTypeToString = {
    SpookStationDeviceType.EMFReader: "EMF Reader",
    SpookStationDeviceType.SpiritBox: "Spirit Box"
}


SpookStationDeviceStringToType = {v: k for k, v in SpookStationDeviceTypeToString.items()}


class SpookStationDeviceConnectionState(Enum):
	Connected = 1
	PoorConnection = 2
	Disconnected = 3


class SpookStationSignalType(Enum):
      State = 1
      Control = 2
