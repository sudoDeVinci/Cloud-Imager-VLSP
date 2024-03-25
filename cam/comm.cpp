#include "comm.h"

/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct whihc is filled by calling getLocalTime().
  * Big thanks to Andreas Spiess:
  * https://github.com/SensorsIot/NTP-time-for-ESP8266-and-ESP32/blob/master/NTP_Example/NTP_Example.ino
  *
  *  If tm_year is not equal to 0xFF, it is assumed that valid time information has been received.
  */
String getTime(tm *timeinfo, time_t *now, int timer) {
  uint32_t start = millis();
  debug("Getting time!");

  do {
    time(now);
    localtime_r(now, timeinfo);
    debug(".");
    delay(150);
  } while (((millis() - start) <= (1000 * timer)) && (timeinfo -> tm_year <= 1970));
  debugln();
  if (timeinfo -> tm_year == 1970) return "None";

  char timestamp[30];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(now));
  debugln("Got time!");
  return String(timestamp);
}

/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(const char* SSID, const char* PASS, Sensors::Status *stat) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(SSID, PASS);
    WiFi.setSleep(false);
    debugln("Connecting to WiFi Network " + String(SSID));
    int connect_count = 0; 
    // Wait for the WiFi connection to be established with a timeout of 10 attempts.
    while (WiFi.status() != WL_CONNECTED && connect_count < 10) {
        delay(random(150, 550));
        debug(".");
        connect_count+=1;
    }

    if (WiFi.status() != WL_CONNECTED) {
    // Connection attempt failed after 10 tries, print an error message and return 1
    debugln("Could not connect to Wifi.");
    return 1;
  }

    debugln("Connected!: -> " + WiFi.macAddress());
    return 0;
}

void getResponse(HTTPClient *HTTP, int httpCode) {
  if (httpCode > 0) {
        debugf("[HTTP] POST... code: %d\n", httpCode);
        if (httpCode == HTTP_CODE_OK) debug(HTTP -> getString());
  } else debugf("[HTTP] POST... failed, error: %s\n", HTTP -> errorToString(httpCode).c_str());

  debugln();
}

/**
 * Send byte buffer to server via HTTPClient.
 * Got gist of everything from klucsik at:
 * https://gist.github.com/klucsik/711a4f072d7194842840d725090fd0a7
 */
void send(HTTPClient *https, Network *network, const String& timestamp, camera_fb_t *fb) {
  https -> setConnectTimeout(READ_TIMEOUT);
  https -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.IMAGE_JPG);
  https -> addHeader(network -> headers.MAC_ADDRESS, WiFi.macAddress());
  https -> addHeader(network -> headers.TIMESTAMP, timestamp);

  int httpCode = https -> POST(fb -> buf, fb -> len);

  getResponse(https, httpCode);   
}

/**
 * Send image from weather station to server. 
 */
void sendImage(HTTPClient *https, Network *network, camera_fb_t *fb, const String& timestamp) {
  debugln("\n[IMAGE]");
  String url;
  url.reserve(strlen(network -> HOST) + strlen(network -> routes.IMAGE) + 1);
  url.concat(network -> HOST);
  url.concat(network -> routes.IMAGE);

  https -> begin(url, network -> CERT);

  send(https, network, timestamp, fb);
}