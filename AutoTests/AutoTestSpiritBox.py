import sys, os, time
import paho.mqtt.client as mqtt
import traceback
import numpy as np
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStation', 'SpookStationManager'))
sys.path.append(os.path.join(sys.path[0], '..', 'Devices', 'SpiritBox', 'SpiritBoxMQTTClient'))

from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationDeviceConnectionState, SpookStationSignalType
from SpookStationManagerDevices.SpookStationManagerDeviceUtil import SpookStationSignal
from SpiritBoxMQTTClient import SpiritBoxMQTTClient

MQTT_ADDRESS = "localhost"



def wait_until(condition, interval=0.01, timeout=1, *args):
    start = time.time()
    try:
        while not condition(*args):
            if time.time() - start > timeout:
                raise Exception("Timeout")
            time.sleep(interval)
    except Exception as e:
        traceback.print_stack()
        return False, None
    else:
        return True, time.time() - start

mockSpiritBoxName = "SpiritBox1"

dm = SpookStationManager(enableDebugPrints=True)
dm.addDevice(mockSpiritBoxName, SpookStationDeviceType.SpiritBox)

time.sleep(1)

mockSpiritBox = SpiritBoxMQTTClient(deviceName=mockSpiritBoxName, ipAddress = MQTT_ADDRESS, enableDebugPrints = True)

time.sleep(1)

speechVolumeChangeTimings = []
for desiredSpeechVolume in [0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0]:
    dm.devices[mockSpiritBoxName].speechVolume.setValue(desiredSpeechVolume, signalType = SpookStationSignalType.Control)
    condition = lambda: dm.devices[mockSpiritBoxName].speechVolume.getValue(signalType = SpookStationSignalType.State) == desiredSpeechVolume
    result = wait_until(condition=condition , timeout=10)
    assert result[0]
    speechVolumeChangeTimings.append(result[1])
print("Average speech volume change time:", np.mean(speechVolumeChangeTimings), "seconds")

speechRateChangeTimings = []
for desiredSpeechRate in [10, 20, 30, 40, 50, 60, 70, 80, 90, 500]:
    dm.devices[mockSpiritBoxName].speechRate.setValue(desiredSpeechRate, signalType = SpookStationSignalType.Control)
    condition = lambda: dm.devices[mockSpiritBoxName].speechRate.getValue(signalType = SpookStationSignalType.State) == desiredSpeechRate
    result = wait_until(condition=condition , timeout=2)
    assert result[0]
    speechRateChangeTimings.append(result[1])
print("Average speech rate change time:", np.mean(speechRateChangeTimings), "seconds")

availableVoices = dm.devices[mockSpiritBoxName].availableVoices.getValue(signalType = SpookStationSignalType.State).split(",")

voiceChangeTimings = []
for desiredVoice in availableVoices * 2:
    dm.devices[mockSpiritBoxName].voice.setValue(desiredVoice, signalType = SpookStationSignalType.Control)
    condition = lambda: dm.devices[mockSpiritBoxName].voice.getValue(signalType = SpookStationSignalType.State) == desiredVoice
    result = wait_until(condition=condition , timeout=2)
    assert result[0]
    voiceChangeTimings.append(result[1])
print("Average voice change time:", np.mean(voiceChangeTimings), "seconds")

staticVolumeChangeTimings = []
for desiredStaticVolume in [0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 0.0]:
    dm.devices[mockSpiritBoxName].staticVolume.setValue(desiredStaticVolume, signalType = SpookStationSignalType.Control)
    condition = lambda: dm.devices[mockSpiritBoxName].staticVolume.getValue(signalType = SpookStationSignalType.State) == desiredStaticVolume
    result = wait_until(condition=condition , timeout=2)
    assert result[0]
    staticVolumeChangeTimings.append(result[1])
print("Average static volume change time:", np.mean(staticVolumeChangeTimings), "seconds")

staticVolumeWhileTalkingChangeTimings = []
for desiredStaticVolumeWhileTalking in [0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 0.0]:
    dm.devices[mockSpiritBoxName].staticVolumeWhileTalking.setValue(desiredStaticVolumeWhileTalking, signalType = SpookStationSignalType.Control)
    condition = lambda: dm.devices[mockSpiritBoxName].staticVolumeWhileTalking.getValue(signalType = SpookStationSignalType.State) == desiredStaticVolumeWhileTalking
    result = wait_until(condition=condition , timeout=2)
    assert result[0]
    staticVolumeWhileTalkingChangeTimings.append(result[1])
print("Average static volume while talking change time:", np.mean(staticVolumeWhileTalkingChangeTimings), "seconds")

talkingDelayTimings = []
for desiredWordsToSay in ["Hello", "world", "this", "is", "an", "autotest"]:
    dm.devices[mockSpiritBoxName].wordsToSay.setValue(desiredWordsToSay, signalType = SpookStationSignalType.Control)
    condition = lambda: mockSpiritBox.lastWordsSaid == desiredWordsToSay
    result = wait_until(condition=condition , timeout=10)
    assert result[0]
    talkingDelayTimings.append(result[1])
print("Average talking delay time:", np.mean(talkingDelayTimings), "seconds")

dm.destroy()
del mockSpiritBox

print("Autotest successful!")

