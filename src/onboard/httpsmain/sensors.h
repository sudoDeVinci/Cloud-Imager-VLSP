#ifndef SENSORS_H
#define SENSORS_H

#include "esp_camera.h"
#include <Arduino.h>
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>


struct Sensors {
    TwoWire wire;
    Adafruit_BMP3XX BMP;
    Adafruit_SHT31 SHT;
    camera_fb_t *CAM;

    struct Status {
        bool CAM = false;
        bool SHT = false;
        bool BMP = false;
    }status;
};

/**
 * Setup the SHT31-D and return the sensor object.
 */
Adafruit_SHT31 shtSetup(TwoWire *wire, Sensors::Status *stat);

/*
 * Setup and calibrate the BMP390. Return the sensor object.
 */
Adafruit_BMP3XX bmpSetup(TwoWire *wire, Sensors::Status *stat);

/**
 * Scan Serial connection on predefined pins for sensors. Print the addresses in hex. 
 */
void Scan (TwoWire *wire);

/**
 * Set up camera for taking periodic images.
 * Return 1 if good, 0 if failed at some point. 
 */
int cameraSetup(Sensors::Status *stat);

#endif