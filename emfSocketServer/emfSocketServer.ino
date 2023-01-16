#include <string.h>
#include <WiFi.h>

//debug
bool useDebugPrints = true;

//Networking
char* ssid     = "spook-station-dev";
char* password = "spook-station-dev";
WiFiServer wifiServer(80);

//Device data
const char*         deviceInformation = "deviceInfo:EMFReader:EMFReader1:";
int                 state = 0;
 
void setup() 
{
  if (useDebugPrints)
  {
    Serial.begin(115200);

    while (!Serial); // Wait serial
  }

 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    if (useDebugPrints){
      Serial.println("Connecting to WiFi..");
    }
    
  }

  if (useDebugPrints){
    Serial.println("Connected to the WiFi network");
    Serial.println(WiFi.localIP());
  }
  
 
  wifiServer.begin();
}
 
void loop() 
{
  WiFiClient client = wifiServer.available();
 
  if (client) 
  {
    while (client.connected()) 
    {
      if (client.available()>0) 
      {
        String message = readMessage(&client);

        if (isArgumentlessMessage(&message))
        {
          handleArgumentlessMessage(&client, &message);
        }
        else
        {
          handleMessage(&client, &message);
        }
      }
      delay(10);
    }
    client.stop();
    if (useDebugPrints){
      Serial.println("Client disconnected");
    }
    
  }
}

String readMessage(WiFiClient* client){
  String line = client->readStringUntil('\0');
  if (useDebugPrints){
    Serial.println("New message received:" + line);
  }
  
  return line;
}

int isArgumentlessMessage(String* message){
  return message->indexOf(":") == -1 ? true : false;
}

void handleArgumentlessMessage(WiFiClient* client, String* message){
  if (*message == "requestClientName")
  {
    sendClientName(client);
  }
  else if (*message == "requestHeartBeat")
  {
    sendHeartBeat(client);
  }
  else if (*message == "requestState")
  {
    sendClientState(client);
  }
  else
  {
    if (useDebugPrints){
      Serial.println("Unknown argumentless message type:" + *(message));
    }
    
  }
}

void handleMessage(WiFiClient* client, String* message){
  int delimiterPosition = message->indexOf(':');
  String messageType = message->substring(0,delimiterPosition);
  if (messageType == "setClientState")
  {
    if (useDebugPrints){
      Serial.println("Processing setClientState message:" + *message);
    }
    int messageSize = message->length();
    String stateValueString = message->substring(delimiterPosition+1, messageSize);
    int stateValueInt = stateValueString.toInt();
    state = stateValueInt;
    if (useDebugPrints){
      Serial.println("Sending response to message:" + *message);
    }
    sendSetClientStateSuccess(client);
    if (useDebugPrints){
      Serial.println("Sent response to message:" + *message);
    }
  }
  else
  {
    if (useDebugPrints){
      Serial.println("Unknown message type:" + messageType);
    }
    
  }
}

void sendSetClientStateSuccess(WiFiClient* client){
  sendClientState(client);
}

void sendClientState(WiFiClient* client){
  String stateName = "clientEMFState";
  String finalMessage = stateName + ":" + state;
  client->println(finalMessage);
  if (useDebugPrints){
    Serial.println("Sending message: " + finalMessage);
  }
  
}

void sendHeartBeat(WiFiClient* client){
  client->println("clientHeartBeat:EMFReader1");
}

void sendClientName(WiFiClient* client){
  client->println(deviceInformation);
}
