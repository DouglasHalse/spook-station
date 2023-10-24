from SpookStationManagerEnums import SpookStationDeviceType, SpookStationSignalType
from SpookStationManagerDevices.SpookStationManagerDeviceBase import SpookStationDeviceBase
from SpookStationManagerDevices.SpookStationManagerDeviceUtil import SpookStationSignal
import random, time, threading

class SpookStationManagerDeviceEMFReader(SpookStationDeviceBase):
    def __init__(self, deviceName: str, useDebugPrints: bool = False) -> None:
        super().__init__(deviceName, SpookStationDeviceType.EMFReader)
        self.state = SpookStationSignal(name="state", 
                                        MQTTStateTopic=deviceName + "/current_state", 
                                        MQTTControlTopic=deviceName + "/desired_state", 
                                        deviceName=deviceName, 
                                        initialValue=0, 
                                        enableDebugPrints=useDebugPrints)   
        self.useSound = SpookStationSignal(name="useSound", 
                                           MQTTStateTopic=deviceName + "/current_use_sound", 
                                           MQTTControlTopic=deviceName + "/desired_use_sound", 
                                           deviceName=deviceName, 
                                           initialValue=False, 
                                           enableDebugPrints=useDebugPrints)
        self.currentStateChangeCallback = None
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
        if self.currentStateChangeCallback != None and self.state.getValue(signalType=SpookStationSignalType.State) != state:
            self.currentStateChangeCallback(state)
        self.state.setValue(state, signalType=SpookStationSignalType.State)

    def getDesiredStateWithFluctuation(self) -> int:
        self.lastGetStateTime = time.time()
        if self._shouldAlterFluctuation():
            desiredStateWithoutFluctuation = self.state.getValue(signalType=SpookStationSignalType.Control)
            alteredState = desiredStateWithoutFluctuation + random.randint(-self.fluctuationMagnitude, self.fluctuationMagnitude)
            if alteredState < 0:
                alteredState = 0
            elif alteredState > 4:
                alteredState = 4
            return alteredState
        return self.state.getValue(signalType=SpookStationSignalType.Control)
        
    def setDesiredUseSound(self, useSound: bool):
        if self.currentUseSoundChangeCallback != None and self.useSound.getValue(signalType=SpookStationSignalType.Control) != useSound:
            self.currentUseSoundChangeCallback(useSound)
        self.useSound.setValue(useSound, signalType=SpookStationSignalType.Control)

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