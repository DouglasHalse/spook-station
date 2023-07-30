from SpookStationManagerEnums import SpookStationDeviceType
from SpookStationManagerDevices.SpookStationManagerDeviceBase import SpookStationDeviceBase
import random, time, threading

class SpookStationManagerDeviceEMFReader(SpookStationDeviceBase):
    def __init__(self, deviceName: str) -> None:
        super().__init__(deviceName, SpookStationDeviceType.EMFReader)
        self.desiredState = 0
        self.currentState = 0
        self.currentStateChangeCallback = None
        self.desiredUseSound = False
        self.currentUseSound = False
        self.currentUseSoundChangeCallback = None
        self.fluctuationRate = 0
        self.fluctuationMagnitude = 0
        self.lastGetStateTime = 0
        self.lastAlteredStateTime = 0
        self.stateTopics = []
        for topicSuffix in ["current_state", "current_use_sound"]:
            self.stateTopics.append(deviceName + "/" + topicSuffix)

    def setOnStateChangeCallback(self, callbackFunction: callable):
        self.currentStateChangeCallback = callbackFunction

    def setOnUseSoundChangeCallback(self, callbackFunction: callable):
        self.currentUseSoundChangeCallback = callbackFunction

    def setCurrentState(self, state: int):
        if self.currentStateChangeCallback != None and self.currentState != state:
            self.currentStateChangeCallback(state)
        self.currentState = state

    def getCurrentState(self) -> int:
        return self.currentState
    
    def setDesiredState(self, state: int):
        self.desiredState = state

    def getDesiredState(self) -> int:
        self.lastGetStateTime = time.time()
        if self._shouldAlterFluctuation():
            alteredState = self.desiredState + random.randint(-self.fluctuationMagnitude, self.fluctuationMagnitude)
            if alteredState < 0:
                alteredState = 0
            elif alteredState > 4:
                alteredState = 4
            return alteredState
        return self.desiredState
    
    def setCurrentUseSound(self, useSound: bool):
        if self.currentUseSoundChangeCallback != None and self.currentUseSound != useSound:
            self.currentUseSoundChangeCallback(useSound)
        self.currentUseSound = useSound

    def getCurrentUseSound(self) -> bool:
        return self.currentUseSound
    
    def setDesiredUseSound(self, useSound: bool):
        self.desiredUseSound = useSound

    def getDesiredUseSound(self) -> bool:
        return self.desiredUseSound
    
    def setFluctuationRate(self, fluctuationRate: int):
        self.fluctuationRate = fluctuationRate

    def getFluctuationRate(self) -> int:
        return self.fluctuationRate
    
    def setFluctuationMagnitude(self, fluctuationMagnitude: int):
        self.fluctuationMagnitude = fluctuationMagnitude

    def getFluctuationMagnitude(self) -> int:
        return self.fluctuationMagnitude
    
    def _shouldAlterFluctuation(self) -> bool:
        timeSinceLastAlter = time.time() - self.lastAlteredStateTime
        if self.fluctuationRate == 0:
            RandVar = random.random()*2
        elif self.fluctuationRate == 1:
            RandVar = random.random()*1
        elif self.fluctuationRate == 2:
            RandVar = random.random()*0.5
        if RandVar < timeSinceLastAlter:
            self.lastAlteredStateTime = time.time()
            return True
        else:
            return False