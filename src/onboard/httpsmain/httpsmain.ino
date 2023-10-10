#include "esp_camera.h"
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>

/**
 * Select camera model
 * #define CAMERA_MODEL_WROVER_KIT
 */

#define CAMERA_MODEL_ESP32S3_EYE

/**
 * Clock speeds for different camera 
*/
#define CAMERA_CLK 20000000


#include "camera_pins.h"
#define MAGNUS_A 17.625
#define MAGNUS_B 243.04

/** 
 * https://metar-taf.com/ESMX
 */
#define SEALEVELPRESSURE_HPA (1020.6)

/**
 * Time to sleep 
 */
#define SLEEP_TIME_MINUTES 10 

/**
 * Define OP CODES for various packets being sent. 
 */
#define READING 0x01
#define REGISTER 0x08
#define SENSORS 0x04
#define IMAGE 0x02

/**
 * Byte array of sensor statuses 
 */
uint8_t STATUSES[11] = {SENSORS, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};


/** ===========================
 *  Enter your WiFi credentials
 *  =========================== 
 *  
 *  Should almost definitely store these on disk but here we are.
 */
const char* SSID = "VLSP-Innovation";
const char* PASS = "9a5mPA8bU64!";
const IPAddress HOST(192, 168, 8, 100);

const uint16_t READINGPORT = 8080;
const uint16_t REGISTERPORT = 8081;
const uint16_t SENSORSPORT = 8082;
const uint16_t IMAGEPORT = 8083;

/**
 * 
 */
WiFiClientSecure client;

/**
 * Attempt to connect to WiFi 10 times.
 * Return 1 if success, return 0 if not. 
 * 
 */
int wifiSetup(void) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASS);
  WiFi.setSleep(false);
  Serial.print("Connecting to WiFi Network .");
  Serial.print(SSID);
  int connect_count = 0; 
  while (WiFi.status() != WL_CONNECTED) {
      delay(random(400, 601));
      Serial.print(".");
      connect_count+=1;
      if (connect_count >= 10) {
          Serial.println("Could not connect to WIfi.");
          return 1;
      }
  }
  Serial.println("");
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  return 0;
}

/**
 *  
 */
int sendStatus(bool * data, size_t lenth) {
    
}