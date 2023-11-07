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
   * network.SSID = "Asimov-2.4GHZ";
   * network.PASS = "Asimov42";
   * TODO: move this onto disk to be loaded later. 
   */
  
  network.CLIENT = &client;
  network.SSID = "VLSP-Innovation";
  network.PASS = "9a5mPA8bU64!";
  network.HOST = IPAddress(192, 168, 8, 99);

  wifiSetup(network.CLIENT, network.SSID, network.PASS, &sensors.status);
  


  sht = Adafruit_SHT31(sensors.wire);
  sensors.SHT = sht;
  shtSetup(sensors.wire, &sensors.status, &sensors.SHT);
  sensors.BMP = bmp;
  bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);
  cameraSetup(&sensors.status);
  
}


void loop() {
  sendStatuses(network.CLIENT, &sensors.status, network.HOST);
  String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  printReadings(readings);
  sendReadings(network.CLIENT, readings, 4, network.HOST);
  delay(5000);
  //Serial.println("Clearing");
  delete[] readings;
}
