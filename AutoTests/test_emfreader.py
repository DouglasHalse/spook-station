import sys
import os
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStation', 'SpookStationManager'))

from AutoTestUtils import wait_until, emfreader_test_setup
from SpookStationManagerEnums import SpookStationSignalType


def test_emfreader_set_state(mosquitto, emfreader_test_setup):
    dm, mockEMFReader = emfreader_test_setup
    for desiredState in [0, 1, 2, 3, 4]:
        dm.devices["MockEMFReader"].state.setValue(desiredState, signalType=SpookStationSignalType.Control)

        emfReaderStateChanged = lambda: mockEMFReader.currentState == desiredState
        assert wait_until(condition=emfReaderStateChanged, timeout=10)

        deviceManagersEMFReaderStateChanged = lambda: dm.devices["MockEMFReader"].state.getValue(signalType=SpookStationSignalType.State) == desiredState
        assert wait_until(condition=deviceManagersEMFReaderStateChanged, timeout=10)

def test_emfreader_set_fluctiation_magnitude(mosquitto, emfreader_test_setup):
    dm, mockEMFReader = emfreader_test_setup
    # Set state to 2, so that the fluctiation magnitude can fluctuate up and down
    dm.devices["MockEMFReader"].state.setValue(2, signalType=SpookStationSignalType.Control)

    # Set fluctuation rate to 2 so that the fluctuation magnitude can fluctuate up and down faster
    dm.devices["MockEMFReader"].fluctuationRate = 2
    for desiredFluctiationMagnitude in [0, 1, 2]:

        dm.devices["MockEMFReader"].fluctuationMagnitude = desiredFluctiationMagnitude

        # Create a dictionary to keep track of the achieved states
        achievedStatesDict = {}
        for wantedStateFluctuation in range(desiredFluctiationMagnitude + 1):
            achievedStatesDict[2 + wantedStateFluctuation] = False
            achievedStatesDict[2 - wantedStateFluctuation] = False

        def allStatesAchieved(achievedStatesDict: dict) -> bool:
            for state in achievedStatesDict:
                if not achievedStatesDict[state]:
                    print("State " + str(state) + " not achieved")
                    return False
            return True
        
        def updateAchievedStatesDict(achievedStatesDict: dict, mockEMFReader):
            achievedStatesDict[mockEMFReader.currentState] = True

        def verifyAllStatesAchieved(achievedStatesDict: dict, mockEMFReader):
            if allStatesAchieved(achievedStatesDict):
                return True
            updateAchievedStatesDict(achievedStatesDict, mockEMFReader)

        emfReaderAllFluctuationMagnitudesAchieved = lambda: verifyAllStatesAchieved(achievedStatesDict, mockEMFReader)
        assert wait_until(condition=emfReaderAllFluctuationMagnitudesAchieved, timeout=10)



def test_emfreader_set_use_sound(mosquitto, emfreader_test_setup):
    dm, mockEMFReader = emfreader_test_setup
    for desiredUseSound in [True, False, True, False, True]:
        dm.devices["MockEMFReader"].useSound.setValue(desiredUseSound, signalType=SpookStationSignalType.Control)

        emfReaderUseSoundChanged = lambda: mockEMFReader.currentUseSound == desiredUseSound
        assert wait_until(condition=emfReaderUseSoundChanged, timeout=10)

        deviceManagersEMFReaderUseSoundChanged = lambda: dm.devices["MockEMFReader"].useSound.getValue(signalType=SpookStationSignalType.State) == desiredUseSound
        assert wait_until(condition=deviceManagersEMFReaderUseSoundChanged, timeout=10)