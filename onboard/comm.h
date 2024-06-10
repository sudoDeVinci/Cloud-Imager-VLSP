#ifndef COMM_H
#define COMM_H

#include "sensors.h"
#include <WiFi.h>
#include <time.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <map>

#define ARDUINOJSON_ENABLE_ARDUINO_STRING 1

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
 * Struct to hold network details in contiguous memory.
 * Many details are read from config files. 
 */
struct NetworkInfo {
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
    const char* INDEX = "/";
    const char* IMAGE = "/api/images";
    const char* REGISTER = "/api/register";
    const char* READING = "/api/reading";
    const char* STATUS = "/api/status";
    const char* UPDATE = "/api/update";
    const char* UPGRADE = "/api/upgrade";
    const char* TEST = "/api/test";
    const char* QNH = "/api/QNH";
  } routes;

  struct Header {
    const String CONTENT_TYPE = "Content-Type";
    const String MAC_ADDRESS = "MAC-Address";
    const String TIMESTAMP = "timestamp"; 
  } headers;
};

/**
 * Set the internal clock via NTP server.
 */
void setClock();

/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct which is filled by calling getLocalTime().
  * Big thanks to Andreas Spiess:
  * https://github.com/SensorsIot/NTP-time-for-ESP8266-and-ESP32/blob/master/NTP_Example/NTP_Example.ino
  *
  *  If tm_year is not equal to 0xFF, it is assumed that valid time information has been received.
  */
String getTime(tm* timeinfo, time_t* now, int timer);

/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(const char* SSID, const char* PASS, Sensors::Status *stat);

/**
 * Get the Sea Level Pressure from the server.
*/
String getQNH(NetworkInfo* network);

/**
 * Parse the QNH from the server response.
 */
String parseQNH(const String& jsonText);

/**
 * Check if the website is reachable before trying to communicate further.
 */
bool websiteReachable(HTTPClient* https, NetworkInfo* network, const String& timestamp);

/**
 * Send statuses of sensors to HOST on specified PORT. 
 */
void sendStats(HTTPClient* https, NetworkInfo* network, Sensors::Status *stat, const String& timestamp);

/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
void sendReadings(HTTPClient* https, NetworkInfo* network, Reading* readings);

/**
 * Send image from weather station to server. 
 */
void sendImage(HTTPClient* https, NetworkInfo* network, camera_fb_t *fb, const String& timestamp);

/**
 * Update the board firmware via the update server.
 */
void OTAUpdate(NetworkInfo* network, const String& version);

#endif // COMM_H