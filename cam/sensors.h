
#ifndef SENSORS_H
#define SENSORS_H

#include "esp_camera.h"
#include <Wire.h>
#include "io.h"



#define CAMERA_CLK 5000000
#define CAMERA_MODEL_ESP32S3_EYE
#define UNDEFINED -69420.00


/**
 * Struct to hold sensor details - pointers and statuses.
 */
struct Sensors {
    camera_fb_t *CAM;
    TwoWire *wire;
    struct Status {
        bool CAM = false;
    } status;
};


/**
 * Deep sleep for a specified number of minutes. 
 */
void deepSleepMins(float mins);

/**
 * Set up the camera. 
 */
void cameraSetup(Sensors::Status *stat);

/**
 * De-init the camera. 
 */
esp_err_t cameraTeardown();


#endif