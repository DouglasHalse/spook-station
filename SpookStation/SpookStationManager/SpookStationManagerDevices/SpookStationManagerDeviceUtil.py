import sys, os
sys.path.append(os.path.join(sys.path[0], '..'))

from SpookStationManagerEnums import SpookStationSignalType

class SpookStationSignal():
    def __init__(self, name: str, MQTTStateTopic: str, MQTTControlTopic: str, deviceName: str, initialValue, enableDebugPrints: bool = False):
        self.name = name
        self.deviceName = deviceName
        self.stateTopic = MQTTStateTopic
        self.controlTopic = MQTTControlTopic
        self.stateValue = initialValue
        self.controlValue = initialValue
        self.initialValue = initialValue
        self.hasChangedState = True
        self.hasChangedControl = True
        self.enableDebugPrints = enableDebugPrints
    
    def debugPrint(self, text: str):
        if self.enableDebugPrints:
            print("SpookStation:\t" + text)	

    def getTopic(self, signalType: SpookStationSignalType) -> str:
        if signalType == SpookStationSignalType.State:
            return self.stateTopic
        elif signalType == SpookStationSignalType.Control:
            return self.controlTopic
        else:
            print("Unknown signal type: " + str(signalType))
            return ""

    def getValue(self, signalType: SpookStationSignalType) -> str:
        if signalType == SpookStationSignalType.State:
            return self.stateValue
        elif signalType == SpookStationSignalType.Control:
            return self.controlValue
        else:
            print("Unknown signal type: " + str(signalType))
            return ""

    def setValue(self, value, signalType: SpookStationSignalType):
        if signalType == SpookStationSignalType.State:
            if self.stateValue != value:
                self.debugPrint("State value changed from " + str(self.stateValue) + " to " + str(value) + " for " + self.deviceName)
                self.hasChangedState = True
            self.stateValue = value
        elif signalType == SpookStationSignalType.Control:
            if self.controlValue != value:
                self.debugPrint("Control value changed from " + str(self.controlValue) + " to " + str(value) + " for " + self.deviceName)
                self.hasChangedControl = True
            self.controlValue = value
        else:
            print("Unknown signal type: " + str(signalType))
    
    def hasChanged(self, signalType: SpookStationSignalType) -> bool:
        if signalType == SpookStationSignalType.State:
            return self.hasChangedState
        elif signalType == SpookStationSignalType.Control:
            return self.hasChangedControl
        else:
            print("Unknown signal type: " + str(signalType))
            return False
        
    def resetHasChanged(self, signalType: SpookStationSignalType):
        if signalType == SpookStationSignalType.State:
            self.hasChangedState = False
        elif signalType == SpookStationSignalType.Control:
            self.hasChangedControl = False
        else:
            print("Unknown signal type: " + str(signalType))

    def resetSignal(self):
        self.stateValue = self.initialValue
        self.controlValue = self.initialValue
        self.hasChangedState = True
        self.hasChangedControl = True