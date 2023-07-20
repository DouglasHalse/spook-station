from SpookStationManagerEnums import SpookStationDeviceType
from SpookStationManagerDevices.SpookStationManagerDeviceBase import SpookStationDeviceBase

class SpookStationManagerDeviceEMFReader(SpookStationDeviceBase):
    def __init__(self, deviceName: str) -> None:
        super().__init__(deviceName, SpookStationDeviceType.EMFReader)
        self.desiredState = 0
        self.currentState = 0
        self.desiredUseSound = False
        self.currentUseSound = False
        self.stateTopics = ["current_state", "current_use_sound"]

    def setCurrentState(self, state: int):
        self.currentState = state

    def getCurrentState(self) -> int:
        return self.currentState
    
    def setDesiredState(self, state: int):
        self.desiredState = state

    def getDesiredState(self) -> int:
        return self.desiredState
    
    def setCurrentUseSound(self, useSound: bool):
        self.currentUseSound = useSound

    def getCurrentUseSound(self) -> bool:
        return self.currentUseSound
    
    def setDesiredUseSound(self, useSound: bool):
        self.desiredUseSound = useSound

    def getDesiredUseSound(self) -> bool:
        return self.desiredUseSound
    
