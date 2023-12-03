#include "sensors.h"
#include "comm.h"

#define FIRMWARE_VERSION "0.0.1"

/**
 * My beautiful globals
 */
Sensors sensors;
Network network;
WiFiClientSecure client;
Adafruit_BMP3XX bmp;
Adafruit_SHT31 sht;
TwoWire wire = TwoWire(0);

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
   * Setting up credentials.
   * ----------------------------------
   * network.SSID = "VLSP-Innovation";
   * network.PASS = "9a5mPA8bU64!";
   * ----------------------------------
   * network.SSID = "Asimov-2.4GHZ";
   * network.PASS = "Asimov42";
   * network.HOST = IPAddress(192, 168, 8, 99);
   * 
   * TODO: move this onto disk to be loaded later. 
   */


  /**
   * Read the profile config for the device network struct. 
   */
  const char* profile = "home.cfg";
  readProfile(SD_MMC, profile, network);// TODO: do something cause the profile reading failed.

  network.CLIENT = &client;
  
  wifiSetup(network.CLIENT, network.SSID, network.PASS, &sensors.status);
  const char* ntpServer = "pool.ntp.org";
  const char* timezone = "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00";
  configTime(0, 0, ntpServer);
  setenv("TZ", timezone, 1);

  OTAUpdate(network, FIRMWARE_VERSION);
  
  sht = Adafruit_SHT31(sensors.wire);
  sensors.SHT = sht;
  shtSetup(sensors.wire, &sensors.status, &sensors.SHT);
  sensors.BMP = bmp;
  bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);
  cameraSetup(&sensors.status);
}


void loop() {

  String timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);

  camera_fb_t * fb = NULL;
  sensors.status.CAM = true;
  fb = esp_camera_fb_get();
  if(!fb) {
    debugln("Camera capture failed");
    sensors.status.CAM = false;
  }
  if(sensors.status.CAM) sendImage(network.CLIENT, fb, network.HOST, timestamp);
  esp_camera_fb_return(fb);
  delay(50);

  sendStatuses(network.CLIENT, &sensors.status, network.HOST, timestamp);
  delay(50);

  String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  sendReadings(network.CLIENT, readings, 4, network.HOST, timestamp);
  delete[] readings;
  delay(50);

  OTAUpdate(network, FIRMWARE_VERSION);
  delay(50);

  debugln("Going to sleep!...");
  delay(50);
  sleep_mins(5);
}

void sleep_mins(float mins) {
  esp_sleep_enable_timer_wakeup(mins*60000000); //10 seconds
  esp_deep_sleep_start();
}

void captureImage(camera_fb_t * fb, Sensors::Status *status) {
  // Take Picture with Camera
  fb = esp_camera_fb_get();  

  if(!fb) {
    debugln("Camera capture failed");
    status ->CAM = false;
    return;
  }

  status ->CAM = true;
  return;
}
