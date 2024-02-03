#include "comm.h"

#define FIRMWARE_VERSION "0.0.1.0"

/**
 * My beautiful globals
 */
Network network;
HTTPClient http;
WiFiClient client;
Adafruit_BMP3XX bmp;
Adafruit_SHT31 sht;
TwoWire wire = TwoWire(0);
Sensors sensors;

void setup() {
  Serial.begin(115200);
  debugln();
  debugln("Setting up.");

  sdmmcInit();

  /**
   * wire.begin(sda, scl)
   * 32,33 for ESP32 "S1" WROVER
   * 41,42 for ESP32 S3
   */
  sensors.wire = &wire;
  sensors.wire -> begin(41,42);

  /**
   * Read the profile config for the device network struct. 
   */
  const char* profile = "server.cfg";
  readProfile(SD_MMC, profile, network);// TODO: do something cause the profile reading failed.

  network.HTTP = &http;
  network.CLIENT = &client;
  
  wifiSetup(network.SSID, network.PASS, &sensors.status);
  //network.CLIENT -> setInsecure();

  const char* ntpServer = "pool.ntp.org";
  const char* timezone = "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00";
  configTime(0, 0, ntpServer);
  setenv("TZ", timezone, 1);

  OTAUpdate(&network, FIRMWARE_VERSION);
  
  sht = Adafruit_SHT31(sensors.wire);
  sensors.SHT = sht;
  shtSetup(sensors.wire, &sensors.status, &sensors.SHT);
  sensors.BMP = bmp;
  bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);
  //esp_err_t deinitErr = cameraTeardown();
  //if (deinitErr != ESP_OK) debugf("Camera init failed with error 0x%x", deinitErr);
  cameraSetup(&sensors.status);
}

void loop() {

  String timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);

  /**
  * Send sensor statuses.
  */
  sendStats(&network, &sensors.status, timestamp);
  delay(50);

  /**
  * Send readings from the other sensors.
  */
  String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  delay(50);
  sendReadings(&network, readings, timestamp);
  delete[] readings;
  delay(50);
  

  /**
  * If camera is up, send and release image buffer. 
  */
  
  if(sensors.status.CAM) {
    camera_fb_t * fb = NULL;
    fb = esp_camera_fb_get();
    sendImage(&network, fb, timestamp);
    esp_camera_fb_return(fb);
    esp_err_t deinitErr = cameraTeardown();
    if (deinitErr != ESP_OK) debugf("Camera init failed with error 0x%x", deinitErr);
  } 

  delay(50);

  OTAUpdate(&network, FIRMWARE_VERSION);
  delay(50);

  debugln("Going to sleep!...");
  delay(50);
  deepSleepMins(5);
}