import time
import pytest
import os, sys

def wait_until(condition, interval=0.01, timeout=1, *args) -> bool:
    start = time.time()
    try:
        while not condition(*args):
            if time.time() - start > timeout:
                raise Exception("Timeout")
            time.sleep(interval)
    except Exception as e:
        return False
    else:
        return True


@pytest.fixture(scope="module")
def spirit_box_test_setup():
    sys.path.append(os.path.join(sys.path[0], '..', 'Devices', 'SpiritBox', 'SpiritBoxMQTTClient'))
    sys.path.append(os.path.join(sys.path[0], '..', 'SpookStation', 'SpookStationManager'))
    from SpiritBoxMQTTClient import SpiritBoxMQTTClient
    from SpookStationManager import SpookStationManager
    from SpookStationManagerEnums import SpookStationDeviceType
    dm = SpookStationManager(enableDebugPrints=True)
    mockSpiritBoxName = "MockSpiritBox"
    dm.addDevice(mockSpiritBoxName, SpookStationDeviceType.SpiritBox)
    time.sleep(1)
    mockSpiritBox = SpiritBoxMQTTClient(deviceName=mockSpiritBoxName, ipAddress="localhost", enableDebugPrints=True)
    time.sleep(1)
    yield dm, mockSpiritBox
    dm.destroy()