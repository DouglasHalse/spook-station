from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from enum import Enum

class FunctionButton(Button):
    def SetFunction(self, function):
        self.on_press = function
        self.text = function.__name__

def GetNewFunctionButton():
    new_button = FunctionButton()
    return new_button   

input_types = {
    'button': GetNewFunctionButton
}

class ConnectionState(Enum):
    DISCONNECTED = 0
    POOR_CONNECTION = 1
    CONNECTED = 2

class BaseDeviceInfoLableWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.ids.deviceName.text = deviceName

class BaseDeviceConnectionIndicatorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def SetColor(self, state : ConnectionState):
        match state:
            case ConnectionState.DISCONNECTED:
                self.ids.color.rgba = 1,0,0,1
            case ConnectionState.POOR_CONNECTION:
                self.ids.color.rgba = 1,1,0,1
            case ConnectionState.CONNECTED:
                self.ids.color.rgba = 0,1,0,1

class BaseDeviceInfoWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(BaseDeviceInfoLableWidget(deviceName=deviceName))
        self.add_widget(BaseDeviceConnectionIndicatorWidget())

class DeviceRowWidget(BoxLayout):
    def __init__(self, deviceName : str, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(BaseDeviceInfoWidget(deviceName=deviceName))

    def AddInput(self, input):
        new_input = input_types[input['input_type']]()
        new_input.SetFunction(input['function'])
        self.add_widget(new_input)

    def Remove(self):
        self.parent.remove_widget(self)

class SpookStationWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SpookStationWidget, self).__init__(**kwargs)
        self.AddNewDeviceInfoWidget("EMF_READER_1")
        self.AddNewDeviceInfoWidget("EMF_READER_2")
        self.AddNewDeviceInfoWidget("EMF_READER_3")
        self.AddNewDeviceInfoWidget("EMF_READER_4")

    def AddNewDeviceInfoWidget(self, deviceName):
        newDeviceRowWidget = DeviceRowWidget(deviceName=deviceName)
        self.ids.deviceList.add_widget(newDeviceRowWidget)

class SpookStationApp(App):
    def build(self):
        self.title = 'SpookStation'
        return SpookStationWidget()


if __name__ == '__main__':
    SpookStationApp().run()