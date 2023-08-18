import sys, os
sys.path.append(os.path.join(sys.path[0], '..'))
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationSignalType
from SpookStationManagerDevices.SpookStationManagerDeviceBase import SpookStationDeviceBase
from SpookStationManagerDevices.SpookStationManagerDeviceUtil import SpookStationSignal


class SpookStationManagerDeviceSpiritbox(SpookStationDeviceBase):
    def __init__(self, deviceName: str) -> None:
        super().__init__(deviceName, SpookStationDeviceType.SpiritBox)
        self.speechVolume = SpookStationSignal(name="speechVolume", 
                                               MQTTStateTopic=deviceName + "/getVolume", 
                                               MQTTControlTopic=deviceName + "/setVolume", 
                                               deviceName=deviceName, 
                                               initialValue=1.0, 
                                               enableDebugPrints=self.enableDebugPrints)
        self.speechRate = SpookStationSignal(name="speechRate", 
                                             MQTTStateTopic=deviceName + "/getRate", 
                                             MQTTControlTopic=deviceName + "/setRate", 
                                             deviceName=deviceName, 
                                             initialValue=300,
                                             enableDebugPrints=self.enableDebugPrints)
        self.availableVoices = SpookStationSignal(name="availableVoices", 
                                                  MQTTStateTopic=deviceName + "/availableVoices", 
                                                  MQTTControlTopic=deviceName + "/availableVoices", 
                                                  deviceName=deviceName, 
                                                  initialValue="",
                                                  enableDebugPrints=self.enableDebugPrints)
        self.voice = SpookStationSignal(name="voice", 
                                        MQTTStateTopic=deviceName + "/getVoice", 
                                        MQTTControlTopic=deviceName + "/setVoice", 
                                        deviceName=deviceName, 
                                        initialValue="english",
                                        enableDebugPrints=self.enableDebugPrints)
        self.staticVolume = SpookStationSignal(name="staticVolume", 
                                               MQTTStateTopic=deviceName + "/getStaticVolume", 
                                               MQTTControlTopic=deviceName + "/setStaticVolume", 
                                               deviceName=deviceName, 
                                               initialValue=0.1,
                                               enableDebugPrints=self.enableDebugPrints)
        self.staticVolumeWhileTalking = SpookStationSignal(name="staticVolumeWhileTalking", 
                                                           MQTTStateTopic=deviceName + "/getStaticVolumeWhileTalking", 
                                                           MQTTControlTopic=deviceName + "/setStaticVolumeWhileTalking", 
                                                           deviceName=deviceName, 
                                                           initialValue=0.1,
                                                           enableDebugPrints=self.enableDebugPrints)
        self.wordsToSay = SpookStationSignal(name="wordsToSay", 
                                             MQTTStateTopic=deviceName + "/say", 
                                             MQTTControlTopic=deviceName + "/say", 
                                             deviceName=deviceName, 
                                             initialValue="",
                                             enableDebugPrints=self.enableDebugPrints)

        self.stateTopics = []
        for topicSuffix in ["getVolume", "getRate", "getVoice", "availableVoices", "getStaticVolume", "getStaticVolumeWhileTalking"]:
            self.stateTopics.append(deviceName + "/" + topicSuffix)

    def hasWordsToSay(self) -> bool:
        if self.wordsToSay.getValue(signalType=SpookStationSignalType.Control) != "":
            return True
        else:
            return False