#ifndef SENSORS_H
#define SENSORS_H

#include "esp_camera.h"
#include <Arduino.h>
#include "Adafruit_Sensor.h"
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>

/**
 * Clock speeds for different camera 
*/

#define MAGNUS_A 17.625
#define MAGNUS_B 243.04
/** 
 * https://metar-taf.com/ESMX
 */
#define SEALEVELPRESSURE_HPA (1020.6)
#define CAMERA_CLK 20000000
#define CAMERA_MODEL_ESP32S3_EYE


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
    }status;
};

/**
 * Setup the SHT31-D and return the sensor object.
 */
void shtSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_SHT31 *sht);

/*
 * Setup and calibrate the BMP390. Return the sensor object.
 */
void bmpSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_BMP3XX *bmp);

/**
 * Scan Serial connection on predefined pins for sensors. Print the addresses in hex. 
 */
void Scan (TwoWire *wire);

/**
 * Set up camera for taking periodic images.
 * Return 1 if good, 0 if failed at some point. 
 */
void cameraSetup(Sensors::Status *stat);

/**
 * Read the humidity from the SHT-31D in rel percent. Return a String.
 */
void read(Adafruit_SHT31 *sht, float *hum);

/**
 * Read the Temperature and pressure from the BMP390 in deg C and hPa.
 */
void read(Adafruit_BMP3XX *bmp, double* out);

String calcDP(double temperature, float humidity, double pressure, double altitude);

String* readAll(Sensors::Status *stat, Adafruit_SHT31 *sht, Adafruit_BMP3XX *bmp);

#endif