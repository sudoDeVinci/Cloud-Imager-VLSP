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
  OTAUpdate(network, FIRMWARE_VERSION);
  String timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);
  sendStatuses(network.CLIENT, &sensors.status, network.HOST, timestamp);
  String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  if(DEBUG) printReadings(readings);
  sendReadings(network.CLIENT, readings, 4, network.HOST, timestamp);
  delete[] readings;
  delay(10);
  sleep_mins(5);
}

void sleep_mins(float mins) {
  esp_sleep_enable_timer_wakeup(mins*60000000); //10 seconds
  esp_light_sleep_start();
}
