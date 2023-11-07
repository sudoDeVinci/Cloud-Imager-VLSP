#ifndef COMM_H
#define COMM_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "sensors.h"
//#include "esp_camera.h"

enum class Ports: uint16_t {
    READINGPORT = 8080,
    REGISTERPORT = 8081,
    SENSORSPORT = 8082,
    IMAGEPORT = 8083
};


enum class MIMEType {
    IMAGE_PNG,
    IMAGE_JPG,
    APP_FORM
};


enum HeaderFields { 
    POST,
    HOST,
    MIME,
    CONNECTION,
    LENGTH,
    MAC,
    TIMESTAMP
};


struct Network {
    const char* SSID;
    const char* PASS;
    const char* CERT;
    IPAddress HOST;
    IPAddress GATEWAY;
    IPAddress DNS;
    WiFiClientSecure CLIENT;
};


/**
 * Connect to a HTTPS server.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, uint16_t PORT);


/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(WiFiClientSecure *client, const char* SSID, const char* PASS, Sensors::Status *stat);


/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
int sendReadings(WiFiClientSecure *client, String* readings, int length, IPAddress HOST);


/**
 * Send statuses of weather sensors to HOST on specified PORT. 
 */
int sendStatuses(WiFiClientSecure *client, Sensors::Status *stat, IPAddress HOST);


/**
 * Send Image buffer to HOST on specified PORT.
*/
int sendImage(WiFiClientSecure *client, camera_fb_t *fb, IPAddress HOST);


/**
 * Generate a header for a given HTTPS packet.
 */
String generateHeader(MIMEType type, int bodyLength, IPAddress HOST, String macAddress);


/**
 * Generate a header for a given HTTPS packet.
 * Some functions return size_t and therefore must be converted.
 * size_t can overflow int as its larger, but we only have 12MB of RAM, and the max image res
 * is like 720p.
 */
String generateHeader(MIMEType type, size_t bodyLength, IPAddress HOST, String macAddress);

/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct whihc is filled by calling getLocalTime().
  */
String getTime();


#endif