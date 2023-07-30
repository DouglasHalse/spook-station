import sys, os, threading
from functools import partial
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStationMQTTManager'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationDeviceConnectionState

from enum import Enum

deviceManager = SpookStationManager()

class EMFReaderWidget(BoxLayout):
    def __init__(self, deviceName, **kwargs):
        super().__init__(**kwargs)
        self.deviceName = deviceName
        for led in range(1, 5):
            self.ids['led' + str(led)].canvas.opacity = .5

    def OnLedNumChanged(self, numLed):
        numLed = int(numLed)
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].setDesiredState(numLed)

    def SetCanvasLedCanvasOpacity(self, led, opacity, *largs):
        self.ids['led' + str(led)].canvas.opacity = opacity
        self.ids['led' + str(led)].canvas.ask_update()

    def SetLedState(self, ledState):
        for led in range(1, 5):
            opacity = 1 if  led <= ledState else  .5
            Clock.schedule_once(partial(self.SetCanvasLedCanvasOpacity, led, opacity ), -1)

    def setUseSoundActive(self, useSound, *largs):
        if useSound == True:
            self.ids["muteButton"].text = "Mute"
        else:
            self.ids["muteButton"].text = "Unmute"

    def SetUseSound(self, useSound):
        Clock.schedule_once(partial(self.setUseSoundActive, useSound), -1)

    def OnFluctuationMagnitudeChanged(self, magnitude):
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].setFluctuationMagnitude(magnitude)
        print("Magnitude set to " + str(magnitude))

    def OnFluctuationRateChanged(self, rate):
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].setFluctuationRate(rate)
        print("Rate set to " + str(rate))

    def onMuteButtonChange(self):
        currentlyUsingSound = deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].getCurrentUseSound()
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].setDesiredUseSound(not currentlyUsingSound)
        print("Setting use sound to " + str(not currentlyUsingSound))

class GenericDeviceWidget(BoxLayout):
    def __init__(self, deviceType : SpookStationDeviceType, deviceName,  **kwargs):
        super().__init__(**kwargs)
        if deviceType == SpookStationDeviceType.EMFReader:
            self.deviceWidget = EMFReaderWidget(deviceName=deviceName)
            self.add_widget(self.deviceWidget)

class BaseDeviceInfoLableWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.ids.deviceName.text = deviceName

class BaseDeviceConnectionIndicatorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def SetColor(self, state : SpookStationDeviceConnectionState):
        if state == SpookStationDeviceConnectionState.Disconnected:
            self.ids.color.rgba = 1,0,0,1
        elif state == SpookStationDeviceConnectionState.PoorConnection:
            self.ids.color.rgba = 1,1,0,1
        elif state == SpookStationDeviceConnectionState.Connected:
            self.ids.color.rgba = 0,1,0,1
        else:
            print("Unsupported Device state: " + state)

class BaseDeviceInfoWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(BaseDeviceInfoLableWidget(deviceName=deviceName))
        self.add_widget(BaseDeviceConnectionIndicatorWidget())

class DeviceRowWidget(BoxLayout):
    def __init__(self, deviceType : SpookStationDeviceType, deviceName : str = "", **kwargs):
        super().__init__(**kwargs)
        self.baseDeviceInfoWidget = BaseDeviceInfoWidget(deviceName=deviceName)
        self.add_widget(self.baseDeviceInfoWidget)
        self.genericDeviceWidget = GenericDeviceWidget(deviceType=deviceType, deviceName=deviceName)
        self.add_widget(self.genericDeviceWidget)
        deviceManager.devices[deviceManager.getDeviceIndex(deviceName)].setOnStateChangeCallback(self.genericDeviceWidget.deviceWidget.SetLedState)
        deviceManager.devices[deviceManager.getDeviceIndex(deviceName)].setOnUseSoundChangeCallback(self.genericDeviceWidget.deviceWidget.SetUseSound)

    def Remove(self):
        self.parent.remove_widget(self)

class SpookStationWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SpookStationWidget, self).__init__(**kwargs)
        deviceManager.addDevice("EMFReader1", SpookStationDeviceType.EMFReader)
        self.AddNewDeviceInfoWidget(deviceType=SpookStationDeviceType.EMFReader, deviceName= "EMFReader1")

    def AddNewDeviceInfoWidget(self, deviceType, deviceName):
        newDeviceRowWidget = DeviceRowWidget(deviceType=deviceType, deviceName=deviceName)
        self.ids.deviceList.add_widget(newDeviceRowWidget)

class SpookStationApp(App):
    def build(self):
        self.title = 'SpookStation'
        return SpookStationWidget()


if __name__ == '__main__':
    SpookStationApp().run()