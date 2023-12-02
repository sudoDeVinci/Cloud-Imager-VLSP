#ifndef COMM_H
#define COMM_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
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