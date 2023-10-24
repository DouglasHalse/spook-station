import sys, os, threading
from functools import partial
sys.path.append(os.path.join(sys.path[0], '..', 'SpookStationManager'))
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
from SpookStationManager import SpookStationManager
from SpookStationManagerEnums import SpookStationDeviceType, SpookStationDeviceConnectionState, SpookStationSignalType, SpookStationDeviceTypeToString, SpookStationDeviceStringToType
from enum import Enum

deviceManager = SpookStationManager(enableDebugPrints=True, useCyclicControlSignalPublishing=True)


def verifyDeviceName(deviceName: str):
    registeredDeviceNames = [device.deviceName for device in deviceManager.getRegisteredDevices()]
    if deviceName in registeredDeviceNames:
        deviceNameNotRegisteredErrorMessagePopup = ErrorMessagePopup(errorMessage="Device with name " + deviceName + " already registered")
        deviceNameNotRegisteredErrorMessagePopup.open()
        return False
    return True


def verifyDeviceType(deviceType: SpookStationDeviceType):
    if deviceType not in [SpookStationDeviceType.EMFReader]:
        deviceTypeString = SpookStationDeviceTypeToString[deviceType]
        deviceTypeNotSupportedErrorMessagePopup = ErrorMessagePopup(errorMessage="Device type " + deviceTypeString + " not supported (yet)")
        deviceTypeNotSupportedErrorMessagePopup.open()
        return False
    return True


class ImageButton(ButtonBehavior, Image):
    pass


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EMFReaderWidget(BoxLayout):
    def __init__(self, deviceName, **kwargs):
        super().__init__(**kwargs)
        self.deviceName = deviceName
        for led in range(1, 5):
            self.ids['led' + str(led)].canvas.opacity = .5
        deviceManager.devices[deviceName].setOnStateChangeCallback(self.SetLedState)
        deviceManager.devices[deviceName].setOnUseSoundChangeCallback(self.SetUseSound)
        self.canvasOpacity = 0

    def OnLedNumChanged(self, numLed):
        numLed = int(numLed)
        deviceManager.devices[self.deviceName].state.setValue(numLed, signalType=SpookStationSignalType.Control)

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
        deviceManager.devices[self.deviceName].fluctuationMagnitude = magnitude
        print("Magnitude set to " + str(magnitude))

    def OnFluctuationRateChanged(self, rate):
        deviceManager.devices[self.deviceName].fluctuationRate = rate
        print("Rate set to " + str(rate))

    def OnMuteButtonChange(self):
        currentlyUsingSound = deviceManager.devices[self.deviceName].useSound.getValue(signalType=SpookStationSignalType.State)
        deviceManager.devices[self.deviceName].setDesiredUseSound(useSound = not currentlyUsingSound)
        print("Setting use sound to " + str(not currentlyUsingSound))


class GenericDeviceWidget(BoxLayout):
    def __init__(self, deviceType: SpookStationDeviceType, deviceName,  **kwargs):
        super().__init__(**kwargs)
        if deviceType == SpookStationDeviceType.EMFReader:
            self.deviceWidget = EMFReaderWidget(deviceName=deviceName)
            self.setGrayedOut(grayedOut=True)
            self.add_widget(self.deviceWidget)
        else:
            print("Unsupported Device Type: " + str(deviceType))

    def setGrayedOut(self, grayedOut: bool):
        if grayedOut:
            self.deviceWidget.canvasOpacity = .5
            self.deviceWidget.disabled = True
        else:
            self.deviceWidget.canvasOpacity = 0
            self.deviceWidget.disabled = False


class BaseDeviceInfoLableWidget(BoxLayout):
    def __init__(self, deviceName: str, **kwargs):
        super().__init__(**kwargs)
        self.ids.deviceName.text = deviceName


class BaseDeviceConnectionIndicatorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
 
    def SetColor(self, state: SpookStationDeviceConnectionState, *largs):
        if state == SpookStationDeviceConnectionState.Disconnected:
            self.ids['deviceConnectionIndicator'].source = "Images/ghost_red.png"
        elif state == SpookStationDeviceConnectionState.PoorConnection:
            self.ids['deviceConnectionIndicator'].source = "Images/ghost_yellow.png"
        elif state == SpookStationDeviceConnectionState.Connected:
            self.ids['deviceConnectionIndicator'].source = "Images/ghost_green.png"
        else:
            print("Unsupported Device state: " + state)


class BaseDeviceInfoWidget(BoxLayout):
    def __init__(self, deviceName: str, **kwargs):
        super().__init__(**kwargs)
        self.labelWidget = BaseDeviceInfoLableWidget(deviceName=deviceName)
        self.add_widget(self.labelWidget)
        self.indicatorWidget = BaseDeviceConnectionIndicatorWidget()
        self.add_widget(self.indicatorWidget)


class DeviceRowWidget(BoxLayout):
    def __init__(self, deviceType: SpookStationDeviceType, deviceName: str = "", **kwargs):
        super().__init__(**kwargs)
        self.baseDeviceInfoWidget = BaseDeviceInfoWidget(deviceName=deviceName)
        self.add_widget(self.baseDeviceInfoWidget)
        self.genericDeviceWidget = GenericDeviceWidget(deviceType=deviceType, deviceName=deviceName)
        self.add_widget(self.genericDeviceWidget)
        deviceManager.devices[deviceName].setOnConnectionStateChangeCallback(self.ConnectionStateChangeCallback)

    def ConnectionStateChangeCallback(self, state: SpookStationDeviceConnectionState):
        Clock.schedule_once(partial(self.baseDeviceInfoWidget.indicatorWidget.SetColor, state), -1)
        if state == SpookStationDeviceConnectionState.Disconnected:
            self.genericDeviceWidget.setGrayedOut(grayedOut=True)
        else:
            self.genericDeviceWidget.setGrayedOut(grayedOut=False)

    def Remove(self):
        self.parent.remove_widget(self)


class ManageDevicePopup(Popup):
    def __init__(self, spookStationWidget, manageDevicesPopup, manageDevicesAddedDevice, deviceName, deviceType, **kwargs):
        self.spookStationWidget = spookStationWidget
        self.manageDevicesAddedDevice = manageDevicesAddedDevice
        self.manageDevicesPopup = manageDevicesPopup
        self.deviceName = deviceName
        self.deviceType = deviceType
        super(ManageDevicePopup, self).__init__(**kwargs)
        
    def focus_text_input(self, *largs):
        self.ids.manageDeviceNameInput.focus = True

    def on_open(self):
        self.ids.manageDeviceNameInput.text = self.deviceName
        self.ids.manageDeviceTypeSpinner.values = [SpookStationDeviceTypeToString[deviceType] for deviceType in SpookStationDeviceType]
        self.ids.manageDeviceTypeSpinner.text = SpookStationDeviceTypeToString[self.deviceType]
        Clock.schedule_once(self.focus_text_input, 0)

    def OnConfirmButtonPressed(self, *largs):

        if not verifyDeviceType(SpookStationDeviceStringToType[self.ids.manageDeviceTypeSpinner.text]):
            return
        if not verifyDeviceName(self.ids.manageDeviceNameInput.text):
            return
        # If device name or type changed, remake device
        if self.ids.manageDeviceNameInput.text != self.deviceName or self.ids.manageDeviceTypeSpinner.text != SpookStationDeviceTypeToString[self.deviceType]:
            # Update deviceManager entry
            deviceManager.removeDevice(deviceName=self.deviceName)
            deviceManager.addDevice(deviceName=self.ids.manageDeviceNameInput.text, deviceType=SpookStationDeviceStringToType[self.ids.manageDeviceTypeSpinner.text])

            # Update main list widget entry
            self.spookStationWidget.RemoveDeviceInfoWidget(deviceName=self.deviceName)
            self.spookStationWidget.AddNewDeviceInfoWidget(deviceType=SpookStationDeviceStringToType[self.ids.manageDeviceTypeSpinner.text], deviceName=self.ids.manageDeviceNameInput.text)

            # Update manageDevicesAddedDevice entry
            self.manageDevicesAddedDevice.ids.manageDeviceAddedDeviceName.text = self.ids.manageDeviceNameInput.text
            self.manageDevicesAddedDevice.ids.manageDeviceAddedDeviceType.text = self.ids.manageDeviceTypeSpinner.text
        self.dismiss()

    def OnRemoveButtonPressed(self, *largs):
        # Remove deviceManager entry
        deviceManager.removeDevice(deviceName=self.deviceName)

        # Remove main list widget entry
        self.spookStationWidget.RemoveDeviceInfoWidget(deviceName=self.deviceName)

        # Remove manageDevicesPopup entry
        self.manageDevicesPopup.ids.manageDevicesAddedDevicesGridListContent.remove_widget(self.manageDevicesAddedDevice)

        # Dismiss Manage device Popup
        self.dismiss()


class ManageDevicesPopup(Popup):
    def __init__(self, spookStationWidget,  **kwargs):
        super(ManageDevicesPopup, self).__init__(**kwargs)
        self.spookStationWidget = spookStationWidget
        # Build added devices list from deviceManager
        for device in deviceManager.getRegisteredDevices():
            self.ids.manageDevicesAddedDevicesGridListContent.add_widget(ManageDevicesPopupDevice(spookStationWidget=spookStationWidget, manageDevicesPopup=self, deviceName=device.deviceName, deviceType=device.deviceType))

    def OnAddDeviceButtonPressed(self, *largs):
        addDevicePopup = AddDevicePopup(manageDevicesPopup=self, spookStationWidget=self.spookStationWidget)
        addDevicePopup.open()


class ManageDevicesPopupDevice(BoxLayout):
    def __init__(self, spookStationWidget, manageDevicesPopup, deviceName, deviceType, **kwargs):
        self.spookStationWidget = spookStationWidget
        self.manageDevicesPopup = manageDevicesPopup
        super(ManageDevicesPopupDevice, self).__init__(**kwargs)
        self.ids.manageDeviceAddedDeviceName.text = deviceName
        self.ids.manageDeviceAddedDeviceType.text = SpookStationDeviceTypeToString[deviceType]

    def OnManageDeviceButtonPressed(self, deviceName: str,  *largs):
        deviceType = deviceManager.devices[deviceName].deviceType
        manageDevicePopup = ManageDevicePopup(spookStationWidget=self.spookStationWidget, manageDevicesPopup=self.manageDevicesPopup, manageDevicesAddedDevice=self, deviceName=deviceName, deviceType=deviceType)
        manageDevicePopup.open() 


class AddDevicePopup(Popup):
    def __init__(self, manageDevicesPopup, spookStationWidget, **kwargs):
        super(AddDevicePopup, self).__init__(**kwargs)
        self.manageDevicesPopup = manageDevicesPopup
        self.spookStationWidget = spookStationWidget

    def focus_text_input(self, *largs):
        self.ids.addDeviceNameInput.focus = True

    def on_open(self):
        self.ids.addDeviceTypeSpinner.values = [SpookStationDeviceTypeToString[deviceType] for deviceType in SpookStationDeviceType]
        self.ids.addDeviceTypeSpinner.text = SpookStationDeviceTypeToString[SpookStationDeviceType.EMFReader]
        self.ids.addDeviceNameInput.text = "EMFReader1"
        Clock.schedule_once(self.focus_text_input, 0)

    def AddDevice(self):
        deviceName = self.ids.addDeviceNameInput.text
        deviceTypeText = self.ids.addDeviceTypeSpinner.text
        deviceType = SpookStationDeviceStringToType[deviceTypeText]
        if not verifyDeviceType(deviceType):
            return
        if not verifyDeviceName(deviceName):
            return
        deviceManager.addDevice(deviceName, deviceType)
        self.spookStationWidget.AddNewDeviceInfoWidget(deviceType=deviceType, deviceName=deviceName)
        self.manageDevicesPopup.ids.manageDevicesAddedDevicesGridListContent.add_widget(ManageDevicesPopupDevice(spookStationWidget=self.spookStationWidget, manageDevicesPopup=self.manageDevicesPopup, deviceName=deviceName, deviceType=deviceType))
        self.dismiss()


class ErrorMessagePopup(Popup):
    def __init__(self, errorMessage: str, **kwargs):
        super(ErrorMessagePopup, self).__init__(**kwargs)
        self.ids.errorMessagePopupLabel.text = errorMessage


class SpookStationWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SpookStationWidget, self).__init__(**kwargs)
        self.noAddedDeviceWidget = Image(source="Images/no-added-devices-background.png", allow_stretch=True, keep_ratio=False)
        self.ids.deviceList.add_widget(self.noAddedDeviceWidget)
        deviceManager.bytesReceivedCallback = self.OnBytesReceivedChange
        deviceManager.bytesSentCallback = self.OnBytesSentChange

    def OnBytesReceivedChange(self, bytesReceived, *largs):
        self.ids.bytesReceivedLabel.text = str(bytesReceived)

    def OnBytesSentChange(self, bytesSent, *largs):
        self.ids.bytesSentLabel.text = str(bytesSent)

    def AddNewDeviceInfoWidget(self, deviceType, deviceName):
        # If no added devices widget is in the list, remove it
        if self.noAddedDeviceWidget in self.ids.deviceList.children:
            self.ids.deviceList.remove_widget(self.noAddedDeviceWidget)
        # Add new device info widget
        newDeviceRowWidget = DeviceRowWidget(deviceType=deviceType, deviceName=deviceName)
        self.ids.deviceList.add_widget(newDeviceRowWidget)

    def RemoveDeviceInfoWidget(self, deviceName):
        for deviceRowWidget in self.ids.deviceList.children:
            if deviceRowWidget.baseDeviceInfoWidget.labelWidget.ids.deviceName.text == deviceName:
                self.ids.deviceList.remove_widget(deviceRowWidget)
        if len(self.ids.deviceList.children) == 0:
            self.ids.deviceList.add_widget(self.noAddedDeviceWidget)
        return

    def OnManageDevicesButtonPressed(self, *largs):
        manageDevicesPopup = ManageDevicesPopup(spookStationWidget=self)
        manageDevicesPopup.open()


class SpookStationApp(App):
    def build(self):
        self.title = 'SpookStation'
        return SpookStationWidget()

    def on_stop(self):
        deviceManager.destroy()
        return super().on_stop()


if __name__ == '__main__':
    SpookStationApp().run()