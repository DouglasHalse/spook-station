import sys
import os
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStation', 'SpookStationManager'))

from AutoTestUtils import wait_until, spirit_box_test_setup
from SpookStationManagerEnums import SpookStationSignalType


def test_spiritbox_set_speech_volume(mosquitto, spirit_box_test_setup):
    dm, mockSpiritBox = spirit_box_test_setup
    for desiredSpeechVolume in [0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0]:
        dm.devices["MockSpiritBox"].speechVolume.setValue(desiredSpeechVolume, signalType=SpookStationSignalType.Control)

        spiritBoxSpeechVolumeChanged = lambda: mockSpiritBox.volume == desiredSpeechVolume
        assert wait_until(condition=spiritBoxSpeechVolumeChanged, timeout=10)

        deviceManagersSpiritBoxVolumeChanged = lambda: dm.devices["MockSpiritBox"].speechVolume.getValue(signalType=SpookStationSignalType.State) == desiredSpeechVolume
        assert wait_until(condition=deviceManagersSpiritBoxVolumeChanged, timeout=10)


def test_spiritbox_set_speech_rate(mosquitto, spirit_box_test_setup):
    dm, mockSpiritBox = spirit_box_test_setup
    for desiredSpeechRate in [10, 20, 30, 40, 50, 60, 70, 80, 90, 500]:
        dm.devices["MockSpiritBox"].speechRate.setValue(desiredSpeechRate, signalType=SpookStationSignalType.Control)

        spiritBoxSpeechRateChanged = lambda: mockSpiritBox.rate == desiredSpeechRate
        assert wait_until(condition=spiritBoxSpeechRateChanged , timeout=10)

        deviceManagersSpiritBoxRateChanged = lambda: dm.devices["MockSpiritBox"].speechRate.getValue(signalType=SpookStationSignalType.State) == desiredSpeechRate
        assert wait_until(condition=deviceManagersSpiritBoxRateChanged, timeout=10)


def test_spiritbox_set_speech_voice(mosquitto, spirit_box_test_setup):
    dm, mockSpiritBox = spirit_box_test_setup
    availableVoices = dm.devices["MockSpiritBox"].availableVoices.getValue(signalType=SpookStationSignalType.State).split(",")
    for desiredVoice in availableVoices * 2:
        dm.devices["MockSpiritBox"].voice.setValue(desiredVoice, signalType=SpookStationSignalType.Control)

        spiritBoxVoiceChanged = lambda: mockSpiritBox.voiceIdToName(mockSpiritBox.voice) == desiredVoice
        assert wait_until(condition=spiritBoxVoiceChanged , timeout=10)

        deviceManagersSpiritBoxVoiceChanged = lambda: dm.devices["MockSpiritBox"].voice.getValue(signalType=SpookStationSignalType.State) == desiredVoice
        assert wait_until(condition=deviceManagersSpiritBoxVoiceChanged, timeout=10)


def test_spiritbox_set_static_volume(mosquitto, spirit_box_test_setup):
    dm, mockSpiritBox = spirit_box_test_setup
    for desiredStaticVolume in [0.0, 0.5, 1.0, 0.0, 0.5, 1.0]:
        dm.devices["MockSpiritBox"].staticVolume.setValue(desiredStaticVolume, signalType=SpookStationSignalType.Control)

        spiritBoxStaticVolumeChanged = lambda: mockSpiritBox.staticVolume == desiredStaticVolume
        assert wait_until(condition=spiritBoxStaticVolumeChanged , timeout=10)

        deviceManagersSpiritBoxStaticVolumeChanged = lambda: dm.devices["MockSpiritBox"].staticVolume.getValue(signalType=SpookStationSignalType.State) == desiredStaticVolume
        assert wait_until(condition=deviceManagersSpiritBoxStaticVolumeChanged, timeout=10)


def test_spiritbox_set_static_volume_while_talking(mosquitto, spirit_box_test_setup):
    dm, mockSpiritBox = spirit_box_test_setup
    for desiredStaticVolumeWhileTalking in [0.0, 0.5, 1.0, 0.0, 0.5, 1.0]:
        dm.devices["MockSpiritBox"].staticVolumeWhileTalking.setValue(desiredStaticVolumeWhileTalking, signalType=SpookStationSignalType.Control)

        spiritBoxStaticVolumeWhileTalkingChanged = lambda: mockSpiritBox.staticVolumeWhileTalking == desiredStaticVolumeWhileTalking
        assert wait_until(condition=spiritBoxStaticVolumeWhileTalkingChanged, timeout=10)

        deviceManagersSpiritBoxStaticVolumeWhileTalkingChanged = lambda: dm.devices["MockSpiritBox"].staticVolumeWhileTalking.getValue(signalType=SpookStationSignalType.State) == desiredStaticVolumeWhileTalking
        assert wait_until(condition=deviceManagersSpiritBoxStaticVolumeWhileTalkingChanged, timeout=10)


def test_spiritbox_say(mosquitto, spirit_box_test_setup):
    dm, mockSpiritBox = spirit_box_test_setup
    for desiredSpeech in ["Hello", "world", "this", "is", "an", "autotest"]:
        dm.devices["MockSpiritBox"].wordsToSay.setValue(desiredSpeech, signalType=SpookStationSignalType.Control)

        spiritBoxSpeechChanged = lambda: mockSpiritBox.lastWordsSaid == desiredSpeech
        assert wait_until(condition=spiritBoxSpeechChanged, timeout=10)
