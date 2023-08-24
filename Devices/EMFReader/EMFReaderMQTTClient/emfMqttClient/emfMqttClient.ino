#include <ArduinoMqttClient.h>
#include <WiFi.h>
//#include "arduino_secrets.h"

const int LED1 = 18;
const int LED2 = 17;
const int LED3 = 9;
const int LED4 = 8;
const int LED5 = 7;

const int Buzzer = 6;

const int ledArray[] = {LED1, LED2, LED3, LED4, LED5};

const char* ssid = "spook-station";
const char* pass = "spook-station";

//const char* ssid = "Telia-314B2D";
//const char* pass = "3703C9CF7B";

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char* MQTT_BROKER_IP = "192.168.7.1";
const int MQTT_BROKER_PORT = 1883;

String deviceName = "EMFReader1";
unsigned long lastPublishTime;

unsigned long itterateScanLedTime;
const unsigned long itterateScanLedIntervall = 100;
int currentScanLed = 0;
bool currentScanLedRising = true;

void delayItterateScanLed(unsigned long millisToDelay)
{
  unsigned long targetDelayStop = millis() + millisToDelay;
  while(millis() < targetDelayStop)
  {
    if (millis() > itterateScanLedTime + itterateScanLedIntervall)
    {
      itterateScanLedTime = millis();   // change scheduled time exactly, no slippage will happen
      
      if(currentScanLed == 0)
      {
        currentScanLedRising = true;
        currentScanLed++;
      }
      else if (currentScanLed == 4)
      {
        currentScanLedRising = false;
        currentScanLed--;
      }
      else if (currentScanLedRising)
      {
        currentScanLed++;
      }
      else
      {
        currentScanLed--;
      }
      for(int i = 0; i<5; i++)
      {
        if(i == currentScanLed)
        {
          digitalWrite(ledArray[i], HIGH);
        }
        else
        {
          digitalWrite(ledArray[i], LOW);
        }
      }
    }
  }
  
}

const unsigned long currentStatePublishIntervall = 50; //publish state every 50 milliseconds
int currentState = 0;
bool useSound = true;

String desiredStateTopic = deviceName + "/desired_state";
String currentStateTopic = deviceName + "/current_state";
String desiredUseSoundTopic = deviceName + "/desired_use_sound";
String currentUseSoundTopic = deviceName + "/current_use_sound";

String topics[] = 
{
  desiredStateTopic,
  currentStateTopic,
  desiredUseSoundTopic,
  currentUseSoundTopic
} ;



String receiveString(int messageSize) {
  char messageBuffer[50];
  int counter = 0;
  while (mqttClient.available()) {
    messageBuffer[counter] = (char)mqttClient.read();
    counter++;
  }
  messageBuffer[messageSize] = '\0';
  return String(messageBuffer);
}

bool receiveBool(int messageSize)
{
  char messageBuffer[50];
  int counter = 0;
  while (mqttClient.available()) {
    messageBuffer[counter] = (char)mqttClient.read();
    counter++;
  }
  messageBuffer[messageSize] = '\0';
  String message = String(messageBuffer);
  if(message == String("true") || message == String("True"))
  {
    return true;
  }
  else
  {
    return false;
  }
}

void subscribeToTopics() {
  int nrOfTopics = sizeof(topics)/sizeof(topics[0]);
  for(int i = 0; i < nrOfTopics; i++)
  {
    String topic = topics[i];
    Serial.print("Subscribing to topic: ");
    Serial.println(topic);
    mqttClient.subscribe(topic);
  }
}

void reconnect() {
  Serial.print("Connecting to WIFI: ");
  Serial.println(ssid);
  Serial.print("Connecting");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED)
  {
    delayItterateScanLed(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected to WIFI: ");
  Serial.println(ssid);


  Serial.print("Connecting to MQTT Broker: ");
  Serial.println(MQTT_BROKER_IP);
  Serial.println("Connecting...");
  while (!mqttClient.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT)) {
    itterateScanLed();
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    delayItterateScanLed(100);
    Serial.println("Attempting Reconnect to MQTT Broker...");
  }
  Serial.println();
  Serial.print("Connected to MQTT Broker: ");
  Serial.println(MQTT_BROKER_IP);

  subscribeToTopics();
}

void setup() {
  //Initialize serial and wait for port to open:

  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);

  

  /*Serial.begin(9600);
  while((!Serial))
  {
  #  ;
  #}
  */

  reconnect();

  subscribeToTopics();

  mqttClient.onMessage(onMqttMessage);
}

void loop() {
  if(!mqttClient.connected() or (WiFi.status() != WL_CONNECTED))
  {
    reconnect();
  }

  mqttClient.poll();

  if (millis() > lastPublishTime + currentStatePublishIntervall)
  {
    lastPublishTime = millis();   // change scheduled time exactly, no slippage will happen
    
    mqttClient.beginMessage(currentStateTopic);
    mqttClient.print(currentState);
    mqttClient.endMessage();
    Serial.print("Current state: ");
    Serial.println(currentState);

    mqttClient.beginMessage(currentUseSoundTopic);
    if(useSound)
    {
      mqttClient.print("true");
    }
    else
    {
      mqttClient.print("false");
    }
    mqttClient.endMessage();
    Serial.print("Current use sound: ");
    Serial.println(useSound);
  }

  setLedState(currentState);


}

void itterateScanLed()
{
  if (millis() > itterateScanLedTime + itterateScanLedIntervall)
  {
    itterateScanLedTime = millis();   // change scheduled time exactly, no slippage will happen
    
    if(currentScanLed == 0)
    {
      currentScanLedRising = true;
      currentScanLed++;
    }
    else if (currentScanLed == 4)
    {
      currentScanLedRising = false;
      currentScanLed--;
    }
    else if (currentScanLedRising)
    {
      currentScanLed++;
    }
    else
    {
      currentScanLed--;
    }
  }
}

void setLedState(int state)
{
  int constrainedState = constrain(state, 0, 4);
  for(int i = 0; i <= constrainedState; i++)
  {
    digitalWrite(ledArray[i], HIGH);
  }
  for(int i = constrainedState + 1 ; i < 5; i++)
  {
    digitalWrite(ledArray[i], LOW);
  }

  if (constrainedState == 3 && useSound)
  {
    tone(Buzzer, 5000);
  }
  else if (constrainedState == 4 && useSound)
  {
    tone(Buzzer, 10000);
  }
  else
  {
    noTone(Buzzer);
  }
 }

void onMqttMessage(int messageSize) {
  String messageTopic = mqttClient.messageTopic();

  //Serial.print("Received a message with topic ");
  //Serial.println(messageTopic);

  if (messageTopic == desiredStateTopic)
  {
    String message = receiveString(messageSize);
    int messageInt = message.toInt();
    Serial.print("New desired state: ");
    Serial.println(messageInt);
    currentState = messageInt;
  }
  else if (messageTopic == desiredUseSoundTopic)
  {
    useSound = receiveBool(messageSize);
  }

}
