
#ifndef COMM_H
#define COMM_H

#include <WiFi.h>
#include "sensors.h"
#include "io.h"
#include <time.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include <WiFiClientSecure.h>
#include <map>


/**
 * Ports for various functions.
 */
enum class Port: uint16_t {
    DEF = 8080,
    ALT = 8085,
};

/**
 * Header fields. 
 */
enum class HeaderField {
    CONTENT_TYPE,
    MAC_ADDRESS,
    TIMESTAMP
};



/**
 * Struct to hold network details in continguous memory.
 * Many details are read from config files. 
 */
struct Network {
    const char* SSID;
    const char* PASS;
    const char* CERT;
    const char* HOST;
    IPAddress GATEWAY;
    IPAddress DNS;
    WiFiClientSecure *CLIENT;
    tm TIMEINFO;
    time_t NOW;

    /**
     * MIME types for the different types of packets.
     */
    struct MIMEType {
        const String IMAGE_JPG = "image/jpeg";
        const String APP_FORM = "application/x-www-form-urlencoded";
    } mimetypes;

    /**
     * Routes on the Server. 
     */
    struct Route {
        const char* IMAGE = "/api/images";
        const char* REGISTER = "/api/register";
        const char* READING = "/api/reading";
        const char* STATUS = "/api/status";
        const char* UPDATE = "/api/update";
        const char* UPGRADE = "/api/upgrade";
        const char* TEST = "/api/test";
    } routes;

    struct Header {
        const String CONTENT_TYPE = "Content-Type";
        const String MAC_ADDRESS = "MAC-Address";
        const String TIMESTAMP = "timestamp"; 
    } headers;
};

/**
 * Timeout in milliseconds for connecting to / reading from server.
*/
#define CONN_TIMEOUT 10000
#define READ_TIMEOUT 5000

/**
 * EOL chars used. 
 */
#define CLRF "\r\n"

/**
 * Try to load the config file for a connection profile.
 */
void readProfile(fs::FS &fs, const char *path, Network &network);

/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct whihc is filled by calling getLocalTime().
  * Big thanks to Andreas Spiess:
  * https://github.com/SensorsIot/NTP-time-for-ESP8266-and-ESP32/blob/master/NTP_Example/NTP_Example.ino
  *
  *  If tm_year is not equal to 0xFF, it is assumed that valid time information has been received.
  */
String getTime(tm *timeinfo, time_t *now, int timer);

/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(const char* SSID, const char* PASS, Sensors::Status *stat);

/**
 * Update the board firmware via the update server.
 */
void OTAUpdate(Network *network, String firmware_version);

/**
 * Send statuses of sensors to HOST on specified PORT. 
 */
void sendStats(HTTPClient *https, Network *network, Sensors::Status *stat, const String& timestamp);

/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
void sendReadings(HTTPClient *https, Network *network, String* thpd, const String& timestamp);

/**
 * Send image from weather station to server. 
 */
void sendImage(HTTPClient *https, Network *network, camera_fb_t *fb, const String& timestamp);

#endif
