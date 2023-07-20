from SpookStationManagerEnums import SpookStationDeviceType
from SpookStationManagerDevices.SpookStationManagerDeviceBase import SpookStationDeviceBase

#from SpookStationManagerDeviceBase import SpookStationDeviceBase

class SpookStationManagerDeviceEMFReader(SpookStationDeviceBase):
    def __init__(self, deviceName: str) -> None:
        super().__init__(deviceName, SpookStationDeviceType.EMFReader)
        self.desiredState = 0
        self.currentState = 0

    def handleCurrentStateTopic(self, message: str):
        self.currentState = int(message)