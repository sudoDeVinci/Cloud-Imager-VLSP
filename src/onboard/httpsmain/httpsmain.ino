#include "sensors.h"
#include "comm.h"

/**
 * My beautiful globals
 */
Sensors sensors;
Network network;
WiFiClientSecure client;
Adafruit_BMP3XX bmp;
Adafruit_SHT31 sht;
TwoWire wire = TwoWire(0);


void printReadings(String* readings) {
  Serial.print(readings[0] + " deg C | ");
  Serial.print(readings[1] + " % | ");
  Serial.print(readings[2] + " hPa | ");
  Serial.print(readings[3] + " deg C | ");
  Serial.println();
}


void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up.");

  /**
   * wire.begin(sda, scl)
   * 32,33 for ESP32 "S1" WROVER
   * 41,42 for ESP32 S3
   */
  sensors.wire = &wire;
  sensors.wire -> begin(41,42);


  /**
   * Setting up credentials.
   *
   * network.SSID = "VLSP-Innovation";
   * network.PASS = "9a5mPA8bU64!";
   * TODO: move this onto disk to be loaded later. 
   */
  
  network.SSID = "Asimov-2.4GHZ";
  network.PASS = "Asimov42";
  network.CLIENT = &client;
  
  network.HOST = IPAddress(192, 168, 8, 99);

  wifiSetup(network.CLIENT, network.SSID, network.PASS, &sensors.status);
  const char* ntpServer = "pool.ntp.org";
  const char* timezone = "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00";
  configTime(0, 0, ntpServer);
  setenv("TZ", timezone, 1);



  sht = Adafruit_SHT31(sensors.wire);
  sensors.SHT = sht;
  shtSetup(sensors.wire, &sensors.status, &sensors.SHT);
  sensors.BMP = bmp;
  bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);
  cameraSetup(&sensors.status);
}


void loop() {
  String timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);
  sendStatuses(network.CLIENT, &sensors.status, network.HOST, timestamp);
  String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  printReadings(readings);
  sendReadings(network.CLIENT, readings, 4, network.HOST, timestamp);
  delay(2000);
  delete[] readings;
}
