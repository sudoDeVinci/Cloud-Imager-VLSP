
#ifndef SENSORS_H
#define SENSORS_H

#include "esp_camera.h"
#include "Adafruit_Sensor.h"
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>
#include "io.h"


/**
 * Clock speeds for different camera.
 * Constants for calculations
 * https://metar-taf.com/ESMX 
 */

#define MAGNUS_A 17.625
#define MAGNUS_B 243.04
#define SEALEVELPRESSURE_HPA (1020.6)
#define CAMERA_CLK 5000000
#define CAMERA_MODEL_ESP32S3_EYE
#define UNDEFINED -69420.00


/**
 * Struct to hold sensor details - pointers and statuses.
 */
struct Sensors {
    TwoWire *wire;
    Adafruit_BMP3XX BMP;
    Adafruit_SHT31 SHT;
    camera_fb_t *CAM;

    struct Status {
        bool CAM = false;
        bool SHT = false;
        bool BMP = false;
        bool WIFI = false;
    } status;
};


/**
 * Deep sleep for a specified number of minutes. 
 */
void deepSleepMins(float mins);

/**
 * Setup the SHT31-D and return the sensor object.
 */
void shtSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_SHT31 *sht);

/**
 * Setup and calibrate the BMP390. Return the sensor object.
 */
void bmpSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_BMP3XX *bmp);

/**
 * Set up the camera. 
 */
void cameraSetup(Sensors::Status *stat);

esp_err_t cameraTeardown();

/**
 * Read all sensors for info as Strings. 
 */
String* readAll(Sensors::Status *stat, Adafruit_SHT31 *sht, Adafruit_BMP3XX *bmp);

/**
 * Print the readings for the sesnsors.
 */
void printReadings(String* readings);

#endif