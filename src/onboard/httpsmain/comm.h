#ifndef COMM_H
#define COMM_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "sensors.h"
#include <time.h>
#include "fileio.h"
#include <HTTPUpdate.h>

/**
 * Ports for various functions.
 * This should probably just be one port and multiple paths but I started with this.  
 */
enum class Ports: uint16_t {
    READINGPORT = 8080,
    REGISTERPORT = 8081,
    SENSORSPORT = 8082,
    IMAGEPORT = 8083,
    UPDATEPORT = 8084 
};

/**
 * MIME types for the different types of packets.
 */
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

/**
 * Struct to hold network details read from config files.
 * Cert is read from separate file that config. 
 */
struct Network {
    const char* SSID;
    const char* PASS;
    const char* CERT;
    IPAddress HOST;
    IPAddress GATEWAY;
    IPAddress DNS;
    WiFiClientSecure *CLIENT;
    tm TIMEINFO;
    time_t NOW;
};

/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(WiFiClientSecure *client, const char* SSID, const char* PASS, Sensors::Status *stat);

/**
 * Connect to a HTTPS server.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, uint16_t PORT);


/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
int sendReadings(WiFiClientSecure *client, String* readings, int length, IPAddress HOST, String timestamp);


/**
 * Send statuses of weather sensors to HOST on specified PORT. 
 */
int sendStatuses(WiFiClientSecure *client, Sensors::Status *stat, IPAddress HOST, String timestamp);


/**
 * Send Image buffer to HOST on specified PORT.
*/
int sendImage(WiFiClientSecure *client, camera_fb_t *fb, IPAddress HOST, String timestamp);


/**
 * Generate a header for a given HTTPS packet.
 */
String generateHeader(MIMEType type, int bodyLength, IPAddress HOST, String macAddress, String timestamp);


/**
 * Generate a header for a given HTTPS packet.
 * Some functions return size_t and therefore must be converted.
 * size_t can overflow int as its larger, but we only have 12MB of RAM, and the max image res
 * is like 720p.
 */
String generateHeader(MIMEType type, size_t bodyLength, IPAddress HOST, String macAddress, String timestamp);

/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct whihc is filled by calling getLocalTime().
  */
String getTime(tm *timeinfo, time_t *now, int timer);

/**
 * Read the SSL certificate for a given network into a char array.  
 */
void readCertificateFile(fs::FS &fs, const char *certPath, const char* &certContent);


/**
 * Try to load the config file for a network AP.
 */
bool readServerConf(fs::FS &fs, const char *path, Network &network);


/**
 * Try to load the config file for a network AP.
 */
bool readAPConf(fs::FS &fs, const char *path, Network &network);

/**
 * Try to load the config file for a connection profile.
 */
bool readProfile(fs::FS &fs, const char *path, Network &network);

/**
 * Update the board firmware via the update server.
 */
void OTAUpdate(Network network, String firmware_version);

#endif