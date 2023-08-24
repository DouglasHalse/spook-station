import sys, os, threading
from functools import partial
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStationManager'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationDeviceConnectionState, SpookStationSignalType

from enum import Enum

deviceManager = SpookStationManager()

class EMFReaderWidget(BoxLayout):
    def __init__(self, deviceName, **kwargs):
        super().__init__(**kwargs)
        self.deviceName = deviceName
        for led in range(1, 5):
            self.ids['led' + str(led)].canvas.opacity = .5
        deviceManager.devices[deviceManager.getDeviceIndex(deviceName)].setOnStateChangeCallback(self.SetLedState)
        deviceManager.devices[deviceManager.getDeviceIndex(deviceName)].setOnUseSoundChangeCallback(self.SetUseSound)

    def OnLedNumChanged(self, numLed):
        numLed = int(numLed)
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].state.setValue(numLed, signalType=SpookStationSignalType.Control)

    def SetCanvasLedCanvasOpacity(self, led, opacity, *largs):
        self.ids['led' + str(led)].canvas.opacity = opacity
        self.ids['led' + str(led)].canvas.ask_update()

    def SetLedState(self, ledState):
        for led in range(1, 5):
            opacity = 1 if  led <= ledState else  .5
            Clock.schedule_once(partial(self.SetCanvasLedCanvasOpacity, led, opacity ), -1)

    def SetUseSoundActive(self, useSound, *largs):
        if useSound == True:
            self.ids["muteButton"].text = "Mute"
        else:
            self.ids["muteButton"].text = "Unmute"

    def SetUseSound(self, useSound):
        Clock.schedule_once(partial(self.SetUseSoundActive, useSound), -1)

    def OnFluctuationMagnitudeChanged(self, magnitude):
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].fluctuationMagnitude = magnitude
        print("Magnitude set to " + str(magnitude))

    def OnFluctuationRateChanged(self, rate):
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].fluctuationRate = rate
        print("Rate set to " + str(rate))

    def OnMuteButtonChange(self):
        currentlyUsingSound = deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].useSound.getValue(signalType=SpookStationSignalType.State)
        deviceManager.devices[deviceManager.getDeviceIndex(self.deviceName)].setDesiredUseSound(useSound = not currentlyUsingSound)
        print("Setting use sound to " + str(not currentlyUsingSound))

class GenericDeviceWidget(BoxLayout):
    def __init__(self, deviceType : SpookStationDeviceType, deviceName,  **kwargs):
        super().__init__(**kwargs)
        if deviceType == SpookStationDeviceType.EMFReader:
            self.deviceWidget = EMFReaderWidget(deviceName=deviceName)
            self.add_widget(self.deviceWidget)
        else:
            print("Unsupported Device Type: " + str(deviceType))

class BaseDeviceInfoLableWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.ids.deviceName.text = deviceName

class BaseDeviceConnectionIndicatorWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        deviceManager.devices[deviceManager.getDeviceIndex(deviceName)].setOnConnectionStateChangeCallback(self.ConnectionStateChangeCallback)
        
    def SetColor(self, state : SpookStationDeviceConnectionState, *largs):
        if state == SpookStationDeviceConnectionState.Disconnected:
            self.ids['deviceConnectionIndicator'].source = "Images/ghost_red.png"
        elif state == SpookStationDeviceConnectionState.PoorConnection:
            self.ids['deviceConnectionIndicator'].source = "Images/ghost_yellow.png"
        elif state == SpookStationDeviceConnectionState.Connected:
            self.ids['deviceConnectionIndicator'].source = "Images/ghost_green.png"
        else:
            print("Unsupported Device state: " + state)
    
    def ConnectionStateChangeCallback(self, state : SpookStationDeviceConnectionState):
        Clock.schedule_once(partial(self.SetColor, state), -1)

class BaseDeviceInfoWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(BaseDeviceInfoLableWidget(deviceName=deviceName))
        self.add_widget(BaseDeviceConnectionIndicatorWidget(deviceName=deviceName))

class DeviceRowWidget(BoxLayout):
    def __init__(self, deviceType : SpookStationDeviceType, deviceName : str = "", **kwargs):
        super().__init__(**kwargs)
        self.baseDeviceInfoWidget = BaseDeviceInfoWidget(deviceName=deviceName)
        self.add_widget(self.baseDeviceInfoWidget)
        self.genericDeviceWidget = GenericDeviceWidget(deviceType=deviceType, deviceName=deviceName)
        self.add_widget(self.genericDeviceWidget)

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
    def on_stop(self):
        deviceManager.destroy()
        return super().on_stop()



if __name__ == '__main__':
    SpookStationApp().run()