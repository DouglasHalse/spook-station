#include <string.h>
#include <ESP8266WiFi.h>
#include <WebSocketsServer.h>
#include <string>

void webSocketServerCB(unsigned int num, WStype_t type, uint8_t * payload, size_t length);
void controlLed(uint8_t led, uint8_t state);
void clientResponse(unsigned int num);

struct __attribute__((__packed__)) LedStatus
{
   uint8_t led_1 = 0;
   uint8_t led_2 = 0;
   uint8_t led_3 = 0;
   uint8_t led_4 = 0;
   uint8_t led_5 = 0;
} ledStatus;

const int led_1 = D4; // kollas
const int led_2 = D5; // kollas
const int led_3 = D6; // kollas
const int led_4 = D7; // kollas
const int led_5 = D8; // kollas

//websocket globals
WebSocketsServer socketServer(3950);
bool clientConnected = false;

//debug
bool useDebugPrints = true;

//Networking
char* ssid     = "spook-station-dev";
char* password = "spook-station-dev";

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

  Serial.print("Connecting to ");
  Serial.println(ssid);
  IPAddress ip(10, 10, 1, 11);
  IPAddress gateway(10, 10, 1, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.mode(WIFI_STA);
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if (useDebugPrints){
      Serial.println("Connecting to WiFi..");
    }
    
  }

  if (useDebugPrints){
    Serial.println("Connected to the WiFi network");
    Serial.println(WiFi.localIP());
  }

  socketServer.begin();
  socketServer.onEvent([](unsigned int num, WStype_t type, uint8_t *payload, size_t length)
  {
     return webSocketServerCallback(num, type, payload, length);
  });

  pinMode(led_1, OUTPUT);
  pinMode(led_2, OUTPUT);
  pinMode(led_3, OUTPUT);
  pinMode(led_4, OUTPUT);
  pinMode(led_5, OUTPUT);

  digitalWrite(led_1, 0);
  digitalWrite(led_2, 0);
  digitalWrite(led_3, 0);
  digitalWrite(led_4, 0);
  digitalWrite(led_5, 0);
}
 
void loop() 
{
   socketServer.loop();
}


void webSocketServerCallback(unsigned int num, WStype_t type, uint8_t * payload, size_t length) 
{
    switch(type) 
    {
        case WStype_DISCONNECTED:
            clientConnected = false;
        break;
        case WStype_CONNECTED: 
            clientConnected = true;
        break;
        case WStype_TEXT:
        //message received
        if(length == 2)
        {
           controlLed(payload[0], payload[1]);
           clientResponse(num);
        }
        else
        {
           //felaktigt meddelande
        }

        break;
    }

    return;
}

void clientResponse(unsigned int num)
{
   if(clientConnected)
   {
      socketServer.sendTXT(num, (uint8_t*)&ledStatus, sizeof(LedStatus));
   }
}

void controlLed(uint8_t led, uint8_t state)
{
   Serial.println("controlLed");
   switch(led)
   {
      case 0:
         if(state == 1) 
         {
            ledStatus.led_1 = 1;
         }
         else
         {
            ledStatus.led_1 = 0;
         }
         digitalWrite(led_1, ledStatus.led_1);
      break;
      case 1:
         if(state == 1) 
         {
            ledStatus.led_2 = 1;
         }
         else
         {
            ledStatus.led_2 = 0;
         }
         digitalWrite(led_2, ledStatus.led_2);
      break;
      case 2:
         if(state == 1) 
         {
            ledStatus.led_3 = 1;
         }
         else
         {
            ledStatus.led_3 = 0;
         }
         digitalWrite(led_3, ledStatus.led_3);
      break;
      case 3:
         if(state == 1) 
         {
            ledStatus.led_4 = 1;
         }
         else
         {
            ledStatus.led_4 = 0;
         }
         digitalWrite(led_4, ledStatus.led_4);
      break;
      case 4:
         if(state == 1) 
         {
            ledStatus.led_5 = 1;
         }
         else
         {
            ledStatus.led_5 = 0;
         }
         digitalWrite(led_5, ledStatus.led_5);
      break;
      default:
      ////////////////// felaktigt meddelande
      break;
   }
}

