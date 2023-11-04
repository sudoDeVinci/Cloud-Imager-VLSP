#ifndef SENSORS_H
#define SENSORS_H

#include "esp_camera.h"
#include <Arduino.h>
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>

#define MAGNUS_A 17.625
#define MAGNUS_B 243.04
/** 
 * https://metar-taf.com/ESMX
 */
#define SEALEVELPRESSURE_HPA (1020.6)

/**
 * Clock speeds for different camera 
*/
#define CAMERA_CLK 20000000

struct Sensors {
    TwoWire wire;
    Adafruit_BMP3XX BMP;
    Adafruit_SHT31 SHT;
    camera_fb_t *CAM;

    struct Status {
        bool CAM = false;
        bool SHT = false;
        bool BMP = false;
    } status;
}

#endif