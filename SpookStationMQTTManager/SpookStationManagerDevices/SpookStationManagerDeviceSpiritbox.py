from SpookStationManagerEnums import SpookStationDeviceType
from SpookStationManagerDevices.SpookStationManagerDeviceBase import SpookStationDeviceBase

class SpookStationManagerDeviceSpiritbox(SpookStationDeviceBase):
    def __init__(self, deviceName: str) -> None:
        super().__init__(deviceName, SpookStationDeviceType.SpiritBox)
        self.currentSpeechVolume = 1.0
        self.desiredSpeechVolume = 1.0
        self.currentSpeechRate = 300
        self.desiredSpeechRate = 300
        self.currentLanguage = "swedish"
        self.desiredLanguage = "swedish"
        self.avalableLanguages = []
        self.currentStaticVolume = 0.5
        self.desiredStaticVolume = 0.5
        self.currentStaticVolumeWhileTalking = 0.1
        self.desiredStaticVolumeWhileTalking = 0.1

        self.wordsToSay = ""

        self.currentSpeechVolumeChangeCallback = None
        self.currentSpeechRateChangeCallback = None
        self.currentLanguageChangeCallback = None
        self.avalableLanguagesChangeCallback = None
        self.currentStaticVolumeChangeCallback = None
        self.currentStaticVolumeWhileTalkingChangeCallback = None

        self.stateTopics = []
        for topicSuffix in ["getVolume", "getRate", "getVoice", "availableVoices", "getStaticVolume", "getStaticVolumeWhileTalking"]:
            self.stateTopics.append(deviceName + "/" + topicSuffix)

    def setWordsToSay(self, words: str):
        self.wordsToSay = words

    def hasWordsToSay(self) -> bool:
        if self.wordsToSay != "":
            return True
        else:
            return False

    def consumeWordsToSay(self) -> str:
        wordsToSay = self.wordsToSay
        self.wordsToSay = ""
        return wordsToSay
    
    def setCurrentSpeechVolume(self, speechVolume: float):
        if self.currentSpeechVolumeChangeCallback != None and self.currentSpeechVolume != speechVolume:
            self.currentSpeechVolumeChangeCallback(speechVolume)
        self.currentSpeechVolume = speechVolume

    def getCurrentSpeechVolume(self) -> float:
        return self.currentSpeechVolume

    def setDesiredSpeechVolume(self, speechVolume: float):
        self.desiredSpeechVolume = speechVolume

    def getDesiredSpeechVolume(self) -> float:
        return self.desiredSpeechVolume
    
    def setCurrentSpeechRate(self, speechRate: int):
        if self.currentSpeechRateChangeCallback != None and self.currentSpeechRate != speechRate:
            self.currentSpeechRateChangeCallback(speechRate)

        self.currentSpeechRate = speechRate

    def getCurrentSpeechRate(self) -> int:
        return self.currentSpeechRate

    def setDesiredSpeechRate(self, speechRate: int):
        self.desiredSpeechRate = speechRate

    def getDesiredSpeechRate(self) -> int:
        return self.desiredSpeechRate

    def setCurrentLanguage(self, language: str):
        if self.currentLanguageChangeCallback != None and self.currentLanguage != language:
            self.currentLanguageChangeCallback(language)

        self.currentLanguage = language

    def getCurrentLanguage(self) -> str:
        return self.currentLanguage

    def setDesiredLanguage(self, language: str):
        self.desiredLanguage = language

    def getDesiredLanguage(self) -> str:
        return self.desiredLanguage

    def setAvalableLanguages(self, languages: list):
        if self.avalableLanguagesChangeCallback != None and self.avalableLanguages != languages:
            self.avalableLanguagesChangeCallback(languages)

        self.avalableLanguages = languages

    def getAvalableLanguages(self) -> list:
        return self.avalableLanguages

    def setCurrentStaticVolume(self, staticVolume: float):
        if self.currentStaticVolumeChangeCallback != None and self.currentStaticVolume != staticVolume:
            self.currentStaticVolumeChangeCallback(staticVolume)

        self.currentStaticVolume = staticVolume
    
    def getCurrentStaticVolume(self) -> float:
        return self.currentStaticVolume

    def setCurrentStaticVolumeWhileTalking(self, staticVolume: float):
        if self.currentStaticVolumeWhileTalkingChangeCallback != None and self.currentStaticVolumeWhileTalking != staticVolume:
            self.currentStaticVolumeWhileTalkingChangeCallback(staticVolume)
        
        self.currentStaticVolumeWhileTalking = staticVolume

    def getCurrentStaticVolumeWhileTalking(self) -> float:
        return self.currentStaticVolumeWhileTalking
    
    def setOnChangeCurrentSpeechVolumeChangeCallback(self, callback: callable):
        self.currentSpeechVolumeChangeCallback = callback

    def setOnChangeCurrentSpeechRateChangeCallback(self, callback: callable):
        self.currentSpeechRateChangeCallback = callback

    def setOnChangeCurrentLanguageChangeCallback(self, callback: callable):
        self.currentLanguageChangeCallback = callback

    def setOnChangeAvalableLanguagesChangeCallback(self, callback: callable):
        self.avalableLanguagesChangeCallback = callback

    def setOnChangeCurrentStaticVolumeChangeCallback(self, callback: callable):
        self.currentStaticVolumeChangeCallback = callback

    def SetOnChangeCurrentStaticVolumeWhileTalkingChangeCallback(self, callback: callable):
        self.currentStaticVolumeWhileTalkingChangeCallback = callback