/*
Many thanks to nikxha from the ESP8266 forum
*/

//#include <ESP8266WiFi.h>
#include <SPI.h>
#include <MD5.h>
#include "MFRC522.h"

#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

/* wiring the MFRC522 to ESP8266 (ESP-12)
RST     = GPIO5
SDA(SS) = GPIO4 
MOSI    = GPIO13
MISO    = GPIO12
SCK     = GPIO14
GND     = GND
3.3V    = 3.3V
*/

#define RST_PIN	5  // RST-PIN für RC522 - RFID - SPI - Modul GPIO5 
#define SS_PIN	4  // SDA-PIN für RC522 - RFID - SPI - Modul GPIO4 

const char *ssid =	"***";	    // change according to your Network - cannot be longer than 32 characters!
const char *pass =	"***";	// change according to your Network

MFRC522 mfrc522(SS_PIN, RST_PIN);	// Create MFRC522 instance

void setup() {
  Serial.begin(115200);    // Initialize serial communications
  delay(250);
  Serial.println(F("Booting...."));
  
  SPI.begin();	         // Init SPI bus
  mfrc522.PCD_Init();    // Init MFRC522

  // We start by connecting to a WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  /* Explicitly set the ESP8266 to be a WiFi-client, otherwise, it by default,
     would try to act as both a client and an access-point and could cause
     network-issues with your other WiFi-devices on your WiFi-network. */
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  Serial.println(F("Ready!"));
  Serial.println(F("======================================================")); 
  Serial.println(F("Scan for Card and print UID:"));
}

void loop() { 
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    delay(50);
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }
  // Show some details of the PICC (that is: the tag/card)
  Serial.print(F("Card UID:"));
  unsigned int id = dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
  Serial.println();

    
  WiFiClient client;
  HTTPClient http;
  Serial.print("[HTTP] begin...\n");

  char s[100];

  // create md5 hash of chip id 
  String sid = String(id);
  MD5Builder md5;
  md5.begin();
  md5.add(sid);
  md5.calculate();
  //Serial.println(md5.toString());
  
  //sprintf(s, "http://192.168.8.101:5000/new-coffee?who=%d", id);
  sprintf(s, "http://192.168.1.174:5000/new-coffee?who=%s", md5.toString().c_str());
  if (http.begin(client, s)) {  // HTTP
    Serial.print("[HTTP] GET...\n");
      // start connection and send HTTP header
      int httpCode = http.GET();

      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf("[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = http.getString();
          Serial.println(payload);
        }
      } else {
        Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    } else {
      Serial.printf("[HTTP} Unable to connect\n");
    }
}

// Helper routine to dump a byte array as hex values to Serial
unsigned int dump_byte_array(byte *buffer, byte bufferSize) {
  unsigned int num = 0;
  Serial.print("got new thing with len ");
  Serial.print(bufferSize);
  
  for (byte i = 0; i < bufferSize; i++) {
    num += buffer[i] << 2^i;
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
  Serial.println("converted to: ");
  Serial.println(num);

  return num;
}
