#include "comm.h"

/**
 * Set the internal clock via NTP server.
 */
void setClock() {
  configTime(0, 0, "pool.ntp.org");

  debug(F("Waiting for NTP time sync: "));
  time_t nowSecs = time(nullptr);
  while (nowSecs < 8 * 3600 * 2) {
    delay(500);
    debug(F("."));
    yield();
    nowSecs = time(nullptr);
  }

  debugln();
  struct tm timeinfo;
  gmtime_r(&nowSecs, &timeinfo);
  debug(F("Current time: "));
  debug(asctime(&timeinfo));
}

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
    delay(random(150, 550));
  } while (((millis() - start) <= (1000 * timer)) && (timeinfo -> tm_year <= 1970));
  debugln("Done");
  if (timeinfo -> tm_year == 1970) return "None";

  char timestamp[30];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(now));
  return String(timestamp);
}


/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(NetworkInfo* network, Sensors::Status *stat) {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

  // Read the networkinfo file and get the lisgt of network ssids and passwords.
  String nwinfo = readFile(SD_MMC, "/networkInfo.json");
  JsonDocument jsoninfo;
  deserializeJson(jsoninfo, nwinfo);
  JsonArray networks = jsoninfo["networks"];

  // Scan surrounding networks.
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  int n = WiFi.scanNetworks();
  debugln("Scan done");

  for (int i = 0; i < n; i++) {
    String ssid = WiFi.SSID(i);
    for (JsonVariant networkJson: networks) {
      String networkSSID = networkJson["SSID"];
      String networkPassword = networkJson["PASS"];
      if (ssid == networkSSID) {
        debugln("Connecting to WiFi Network " + ssid);
        WiFi.begin(ssid.c_str(), networkPassword.c_str());

        network -> SSID = networkSSID.c_str();
        network -> PASS = networkPassword.c_str();

        int connect_count = 0; 

        // Wait for the WiFi connection to be established with a timeout of 10 attempts.
        while (WiFi.status() != WL_CONNECTED && connect_count < 10) {
          delay(random(150, 550));
          debug(".");
          connect_count+=1;
        }
      }
    }
  }

  if (WiFi.status() != WL_CONNECTED) {
    // Connection attempt failed after 10 tries, print an error message and return 1
    debugln("Could not connect to Wifi.");
    stat->WIFI = false;
    return 1;
  }

  stat -> WIFI = true;
  debugln("Connected!: -> " + WiFi.macAddress());
  return 0;
}

String getResponse(HTTPClient *HTTP, int httpCode) {
  if (httpCode > 0) return HTTP -> getString();
  else return HTTP -> errorToString(httpCode);
}

/**
 * Send byte buffer to server via HTTPClient.
 * Got gist of everything from klucsik at:
 * https://gist.github.com/klucsik/711a4f072d7194842840d725090fd0a7
 */
void send(HTTPClient* https, NetworkInfo* network, const String& timestamp, uint8_t* buf, size_t len) {
  https -> setConnectTimeout(READ_TIMEOUT);
  https -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.IMAGE_JPG);
  https -> addHeader(network -> headers.MAC_ADDRESS, WiFi.macAddress());
  https -> addHeader(network -> headers.TIMESTAMP, timestamp);

  int httpCode = https -> POST(buf, len);

  debugln(getResponse(https, httpCode));  
}

/**
 * Send message to server via HTTPClient.
 * Got gist of everything from klucsik at:
 * https://gist.github.com/klucsik/711a4f072d7194842840d725090fd0a7
 */
String send(HTTPClient* https, NetworkInfo* network, const String& timestamp) {
    https -> setConnectTimeout(READ_TIMEOUT);
    https -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.APP_FORM);
    https -> addHeader(network -> headers.MAC_ADDRESS, WiFi.macAddress());
    https -> addHeader(network -> headers.TIMESTAMP, timestamp);

    int httpCode = https -> GET();

    return getResponse(https, httpCode);
}

/**
 * Check if the website is reachable before trying to communicate further.
 */
bool websiteReachable(HTTPClient* https, NetworkInfo* network, const String& timestamp) {
  String url;
  url.reserve(strlen(network -> HOST) + strlen(network -> routes.INDEX));
  url.concat(network -> HOST);
  url.concat(network -> routes.INDEX);
  https -> begin(url, network -> CERT);

  int httpCode = https -> GET();

  // Check if the response code is 200 (OK)
  if (httpCode == 200) {
    https -> end();
    debugln("Website reachable");
    return true;
  } else {
    debug("Website unreachable: ");
    debug(https -> errorToString(httpCode));
    https -> end();
    return false;
  }
}

/**
 * Send statuses of sensors to HOST on specified PORT. 
 */
void sendStats(HTTPClient* https, NetworkInfo* network, Sensors::Status *stat, const String& timestamp) {
    debugln("\n[STATUS]");
    const String values ="sht="  + String(stat -> SHT) +
                        "&bmp=" + String(stat -> BMP) +
                        "&cam=" + String(stat -> CAM);

    String url;
    url.reserve(strlen(network -> HOST) + strlen(network -> routes.STATUS) + values.length() + 2);
    url.concat(network -> HOST);
    url.concat(network -> routes.STATUS);
    url.concat("?" + values);

    https -> begin(url, network -> CERT);

    debugln(url);

    String reply = send(https, network, timestamp);
    debugln(reply);
    https -> end();
}

/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
void sendReadings(HTTPClient* https, NetworkInfo* network, Reading* readings) {
  debugln("\n[READING]");

  const String values = "temperature=" + readings -> temperature + 
                        "&humidity=" + readings -> humidity + 
                        "&pressure=" + readings -> pressure + 
                        "&dewpoint=" + readings -> dewpoint;
  
  String url;
  url.reserve(strlen(network -> HOST) + strlen(network -> routes.READING) + values.length() + 2);
  url.concat(network -> HOST);
  url.concat(network -> routes.READING);
  url.concat("?" + values);

  https -> begin(url, network->CERT);

  debugln(url);
  
  String reply = send(https, network, readings -> timestamp);
  debugln(reply);

  https -> end();
}

/**
 * Parse the QNH from the server response.
 */
float parseQNH(const String& jsonText) {
  const char* json = jsonText.c_str();
  JsonDocument doc;

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, json);

  // Test if parsing succeeds.
  if (error) {
    debug("Failed to parse QNH json response error :-> ");
    debug(error.f_str());
    debugln();
    return UNDEFINED;
  }

  float qnh = doc["metar"]["qnh"];
  return qnh;
}

/**
 * Get the Sea Level Pressure from the server.
*/
String getQNH(NetworkInfo* network) {
  debugln("\n[GETTING SEA LEVEL PRESSURE]");

  HTTPClient https;
  const String HOST = "https://api.metar-taf.com";
  const String ROUTE = "/metar";
  const String key = "VOeVgaTHCcmuX4vuOS47tRLPEkOfPWTT";
  const String version = "2.3";
  const String locale = "en-US";
  const String airport = "ESMX";


  const String values = "api_key=" + key + 
                        "&v=" + version + 
                        "&locale=" + locale + 
                        "&id=" + airport + 
                        "&station_id=" + airport + 
                        "&test=0";

  String url;
  url.reserve(HOST.length() + ROUTE.length() + values.length());
  url.concat(HOST);
  url.concat(ROUTE);
  url.concat("?" + values);

  https.begin(url);

  int httpCode = https.GET();

  String reply = getResponse(&https, httpCode);
  
  return reply;
}


/**
 * Send image from weather station to server. 
 */
void sendImage(HTTPClient* https, NetworkInfo* network, uint8_t* buf, size_t len, const String& timestamp) {
  debugln("\n[IMAGE]");
  String url;
  url.reserve(strlen(network -> HOST) + strlen(network -> routes.IMAGE) + 1);
  url.concat(network -> HOST);
  url.concat(network -> routes.IMAGE);

  https -> begin(url, network -> CERT);

  debugln(url);

  send(https, network, timestamp, buf, len);

  https -> end();
}

/**
 * Update the board firmware via the update server.
 */
void OTAUpdate(NetworkInfo* network, const String& firmware_version) {
  debugln("\n[UPDATES]");

  String url;
  url.reserve(strlen(network -> HOST) + strlen(network -> routes.UPDATE) + 1);
  url.concat(network -> HOST);
  url.concat(network -> routes.UPDATE);
  WiFiClient* client = network -> CLIENT;

  // Start the OTA update process
  debug("Grabbing updates from: ");
  debugln(url);
  t_httpUpdate_return ret = httpUpdate.update(*client, url, firmware_version);
  switch (ret) {
    case HTTP_UPDATE_FAILED:
      debugf("HTTP_UPDATE_FAILED Error (%d): %s\n", httpUpdate.getLastError(), httpUpdate.getLastErrorString().c_str());
      break;

    case HTTP_UPDATE_NO_UPDATES:
      debugln("HTTP_UPDATE_NO_UPDATES");
      break;

    case HTTP_UPDATE_OK:
      debugln("HTTP_UPDATE_OK");
      break;
  }
}