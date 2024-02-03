#include "comm.h"

/**
 * Read the SSL certificate for a given network into a char array.  
 */
void readCertificateFile(fs::FS &fs, const char *certPath, const char* &certContent) {

  String pathStr = String(CERT_FOLDER)+"/"+String(certPath);
  File certFile = fs.open(pathStr.c_str());
  if (!certFile) {
      debugln("Failed to open certificate flie " + pathStr);
      return;
  }

  size_t certSize = certFile.size();
  char* tempBuffer = new char[certSize + 1];  // +1 for null-terminator
  if (certFile.readBytes(tempBuffer, certSize) == certSize) {
      tempBuffer[certSize] = '\0';  // Null-terminate the string
      certContent = strdup(tempBuffer);  // Create a dynamically allocated copy
  }
  delete[] tempBuffer;
  certFile.close();
}


/**
 * Try to load the config file for a server.
 */
bool readServerConf(fs::FS &fs, const char *path, Network &network) {
  String pathStr = String(SERVER_FOLDER)+"/"+String(path);
  File file = fs.open(pathStr.c_str());
  if (!file) {
      debugln("Failed to open Server config file");
      return false;
  }

  while (file.available()) {
      String line = file.readStringUntil('\n');
      line.trim();

      if (line.startsWith("HOST")) {
          network.HOST.fromString(line.substring(line.indexOf('=') + 1).c_str());
      } else if (line.startsWith("CERT")) {
          String certFileName = readString(line);
          readCertificateFile(fs, certFileName.c_str(), network.CERT);
      }
  }

  file.close();
  return true;
}


/**
 * Try to load the config file for a network AP.
 */
bool readAPConf(fs::FS &fs, const char *path, Network &network) {
  String pathStr = "/" + String(AP_FOLDER)+"/"+String(path);
  File file = fs.open(pathStr.c_str());
  if (!file) {
      debugln("Failed to open AP config file");
      return false;
  }

  while (file.available()) {
      String line = file.readStringUntil('\n');
      line.trim();

      if (line.startsWith("SSID")) {
          network.SSID = readString(line);
      } else if (line.startsWith("PASS")) {
          network.PASS = readString(line);;
      } else if (line.startsWith("GATEWAY")) {
          network.GATEWAY.fromString(line.substring(line.indexOf('=') + 1).c_str());
      } else if (line.startsWith("DNS")) {
          network.DNS.fromString(line.substring(line.indexOf('=') + 1).c_str());
      }
  }

  file.close();
  return true;
}

/**
 * Try to load the config file for a connection profile.
 */
void readProfile(fs::FS &fs, const char *path, Network &network) {
  String pathStr = String(PROFILE_FOLDER)+"/"+String(path);
  File file = fs.open(pathStr.c_str());
  if (!file) {
    debugln("Failed to open Profile config file");
    return;
  }

  const char* serverPath;
  const char* apPath;

  while (file.available()) {
    String line = file.readStringUntil('\n');
    line.trim();

    // Check if the line starts with "SERVER" or "AP"
    if (line.startsWith("SERVER")) {
      // Extract the file path after the '=' sign
      serverPath = readString(line);
      readServerConf(SD_MMC, serverPath, network);
    } else if (line.startsWith("AP")) {
      // Extract the file path after the '=' sign
      apPath = readString(line);
      readAPConf(SD_MMC, apPath, network);
    }
  }

  file.close();
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
    stat->WIFI = false;
    return 1;
  }

    stat -> WIFI = true;
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
void send(Network *network, const String& timestamp, camera_fb_t *fb) {
  network -> HTTP -> setConnectTimeout(READ_TIMEOUT);
  network -> HTTP -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.IMAGE_JPG);
  network -> HTTP -> addHeader(network -> headers.MAC_ADDRESS, WiFi.macAddress());
  network -> HTTP -> addHeader(network -> headers.TIMESTAMP, timestamp);

  int httpCode = network -> HTTP -> POST(fb -> buf, fb -> len);

  getResponse(network -> HTTP, httpCode);   
}

/**
 * Send message to server via HTTPClient.
 * Got gist of everything from klucsik at:
 * https://gist.github.com/klucsik/711a4f072d7194842840d725090fd0a7
 */
void send(Network *network, const String& timestamp, const String& body) {
    network -> HTTP -> setConnectTimeout(READ_TIMEOUT);
    network -> HTTP -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.APP_FORM);
    network -> HTTP -> addHeader(network -> headers.MAC_ADDRESS, WiFi.macAddress());
    network -> HTTP -> addHeader(network -> headers.TIMESTAMP, timestamp);

    int httpCode = network -> HTTP -> POST(body);

    getResponse(network -> HTTP, httpCode); 
}

/**
 * Send statuses of sensors to HOST on specified PORT. 
 */
void sendStats(Network *network, Sensors::Status *stat, const String& timestamp) {
    debugln("\n[STATUS]");
    const String PATH = String(network->routes.STATUS);
    IPAddress host = network->HOST;
    
    const String body = "?sht="  + String(stat -> SHT) +
                        "&bmp=" + String(stat -> BMP) +
                        "&cam=" + String(stat -> CAM);

    network -> HTTP -> begin(host.toString(), 8080, String(PATH + body));

    debugln(body);

    //send(network, timestamp, body);
    network -> HTTP -> end();

}

/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
void sendReadings(Network *network, String* thpd, const String& timestamp) {
    debugln("\n[READING]");
    const String PATH = String(network->routes.READING);
    IPAddress host = network -> HOST;

    const String body = "?temperature=" + String(thpd[0]) + 
                 "&humidity=" + String(thpd[1]) + 
                 "&pressure=" + String(thpd[2]) + 
                 "&dewpoint=" + String(thpd[3]);

    network -> HTTP -> begin(host.toString(), 8080, String(PATH + body));

    debugln(body);
    
    //send(network, timestamp, body);
    network -> HTTP -> end();
}

/**
 * Send image from weather station to server. 
 */
void sendImage(Network *network, camera_fb_t *fb, const String& timestamp) {
    debugln("\n[IMAGE]");
    const String PATH = String(network->routes.IMAGE);
    IPAddress host = network -> HOST;

    network -> HTTP -> begin(host.toString(), 8080, PATH);

    send(network, timestamp, fb);
    network -> HTTP -> end();
}

/**
 * Update the board firmware via the update server.
 */
void OTAUpdate(Network *network, String firmware_version) {
    debugln("\n[UPDATES]");
    IPAddress host = network -> HOST;

    // Start the OTA update process
    t_httpUpdate_return ret = ESPhttpUpdate.update(String("http://192.168.0.100:8080/update/"), firmware_version);
    switch (ret) {
      case HTTP_UPDATE_FAILED:
        debugf("HTTP_UPDATE_FAILED Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
        break;

      case HTTP_UPDATE_NO_UPDATES:
        debugln("HTTP_UPDATE_NO_UPDATES");
        break;

      case HTTP_UPDATE_OK:
        debugln("HTTP_UPDATE_OK");
        break;
    }
}