#include "sensors.h"
#include "comm.h"

/**
 * My beautiful globals
 */
Sensors sensors;
Network network;



void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up.");

  /**
   * wire.begin(sda, scl)
   * 32,33 for ESP32 "S1" WROVER
   * 41,42 for ESP32 S3
   */
  TwoWire wire = TwoWire(0);
  sensors.wire = &wire;
  wire.begin(41,42);


  /**
   * Setting up credentials.
   * network.SSID = "VLSP-Innovation";
   * network.PASS = "9a5mPA8bU64!";
   * TODO: move this onto disk to be loaded later. 
   */
  network.SSID = "Asimov-2.4GHZ";
  network.PASS = "Asimov42";
  network.HOST = IPAddress(192, 168, 8, 99);

  wifiSetup(&network.CLIENT, network.SSID, network.PASS, &sensors.status);

  if (sensors.status.WIFI == false) {
    ESP.restart();
  }

  /**
   * Setup the camera state.
   */
  cameraSetup(&sensors.status);

  /**
   * Setup the BMP for use.
   */
  sensors.BMP = bmpSetup(sensors.wire, &sensors.status);

  /**
   * Setup the SHT for use.
   */
  sensors.SHT = shtSetup(sensors.wire, &sensors.status);

  /**
   * Set the time by synching with a time server 
   */
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");

  if (sendStatuses(&network.CLIENT, &sensors.status, network.HOST) == 1) {
    Serial.println("Couldn't send stauses.");
    /**
     * TODO: At this point, an interrupt over UART should be sent to the Pico or whatever is being used
     * to wirelessly program the ESP.
     */
  }
}


void loop() {
  String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  Serial.print(readings[0] + " deg C | ");
  Serial.print(readings[1] + " % | ");
  Serial.print(readings[2] + " hPa | ");
  Serial.print(readings[3] + " deg C | ");
}
