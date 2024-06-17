#pragma once
#ifndef SENSORS_H
#define SENSORS_H

#include "io.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "esp_camera.h"
#include "Adafruit_Sensor.h"
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"


/**
 * Clock speeds for different camera.
 * Constants for calculations
 * https://metar-taf.com/ESMX 
 */

#define MAGNUS_A 17.625
#define MAGNUS_B 243.04
#define CAMERA_CLK 5000000
#define CAMERA_MODEL_ESP32S3_EYE
#define UNDEFINED -69420.00
#define SAMPLES 80
#define DISPLAY_WIDTH 128
#define DISPLAY_HEIGHT 64

/**
 * Struct to hold sensor details - pointers and statuses.
 */
struct Sensors {
    TwoWire *wire;
    Adafruit_BMP3XX BMP;
    Adafruit_SHT31 SHT;
    Adafruit_SSD1306 SCREEN;
    camera_fb_t *CAM;

    struct Status {
        bool CAM = false;
        bool SHT = false;
        bool BMP = false;
        bool WIFI = false;
        bool SCREEN = false;
    } status;
};

/**
 * A singular timestamped reading taken by all the sensors.
 */
struct Reading {
    String timestamp = "None";
    String temperature = "None";
    String humidity = "None";
    String pressure = "None";
    String altitude = "None";
    String dewpoint = "None";
};

extern float SEALEVELPRESSURE_HPA;


/**
 * Deep sleep for a specified number of minutes. 
 */
void deepSleepMins(float mins);

/**
 * Setup the SHT31-D and return the sensor object.
 */
void shtSetup(Sensors::Status *stat, Adafruit_SHT31 *sht);

/**
 * Setup and calibrate the BMP390. Return the sensor object.
 */
void bmpSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_BMP3XX *bmp);

/**
 * Set up the camera (OV5640). 
 */
void cameraSetup(Sensors::Status *stat);

/**
 * Reset the OLED display.
 */
void resetDisplay(Adafruit_SSD1306 *display);
 
/**
 * Setup and calibrate the display - Show a welcome message.
 */
void displaySetup(Sensors::Status *stat, Adafruit_SSD1306 *display);

/**
 * Display the readings on the OLED display.
 */
void displayReadings(Reading* readings, Adafruit_SSD1306 *display);

/**
 * Display the statuses of the sensors.
 */
void displayStatuses(Sensors::Status *stat, Adafruit_SSD1306 *display, const char* SSID);

/**
 * De-init the camera. 
 */
esp_err_t cameraTeardown();

/**
 * Read all sensors for info as Strings. 
 */
Reading readAll(Sensors::Status *stat, Adafruit_SHT31 *sht, Adafruit_BMP3XX *bmp);

/**
 * Return string equivalent of float array of readings.
 */
String readingsToString(Reading* readings);

/**
 * Print the readings for the sesnsors.
 */
void printReadings(Reading* readings);

/**
 * Convert a vector a Strings from a csv file to an array of readings.
 */
Reading* csvToReadings(std::vector<String*> csv);

#endif