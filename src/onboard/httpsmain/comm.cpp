#include "comm.h"


String MIMEStr[] = {
    "image/png",
    "image/jpeg",
    "application/x-www-form-urlencoded"
};

String HeaderStr[] = {
  "POST / HTTP/1.1",
  "Host: ",
  "Content-Type: ",
  "Connection: close",
  "Content-Length: ",
  "MAC-address: ",
  "Timestamp: "
};

/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(WiFiClientSecure *client, const char* SSID, const char* PASS, Sensors::Status *stat) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASS);
  WiFi.setSleep(false);
  debugln("Connecting to WiFi Network " + String(SSID));
  int connect_count = 0; 
  while (WiFi.status() != WL_CONNECTED) {
      delay(random(400, 601));
      debug(".");
      connect_count+=1;
      if (connect_count >= 10) {
          debugln("Could not connect to Wifi.");
          stat -> WIFI = false;
          return 1;
      }
  }
  stat -> WIFI = true;
  client -> setInsecure();
  debugln("Connected!");
  return 0;
}


/**
 * Connect to a HTTPS server.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, uint16_t PORT) {
  int conn_count = 0;
  debug("Connecting to Status Server Socket.");
  while (! client -> connect(HOST, PORT)) {
    delay(random(200, 501));
    debug(".");
    conn_count+=1;
    if (conn_count >= 10) {
        debugln("Could not connect to server status socket.");
        return 1;
    }
  }
  debugln("");
  debugln("Connected with client status socket.");
  return 0;
}



/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
int sendReadings(WiFiClientSecure *client, String* readings, int length, IPAddress HOST, String timestamp) {

  String body = "temperature=" + readings[0] + ""\
                "&humidity=" + readings[1] + ""\
                "&pressure=" + readings[2] + ""\
                "&dewpoint=" + readings[3] + "\r\n";

  String header = generateHeader(MIMEType::APP_FORM, body.length(), HOST, WiFi.macAddress(), timestamp);
  if (header == "None") return 1;

  debugln(header);
  debugln(body);
  debugln();

  if (connect(client, HOST, static_cast<uint16_t>(Ports::READINGPORT)) == 1) return 1;

  client -> println(header);
  client -> println(body);
  client -> println();
  client -> stop();

  //body.remove();
  //header.remove();
  return 0;
}


/**
 * Send statuses of weather sensors to HOST on specified PORT. 
 */
int sendStatuses(WiFiClientSecure *client, Sensors::Status *stat, IPAddress HOST, String timestamp) {

  String body = "sht="  + String(stat -> SHT) + ""\
                "&bmp=" + String(stat -> BMP) + ""\
                "&cam=" + String(stat -> CAM)+ "\r\n";

  String header = generateHeader(MIMEType::APP_FORM, body.length(), HOST, WiFi.macAddress(), timestamp);
  if (header == "None") return 1;

  debugln(header);
  debugln(body);
  debugln();

  if (connect(client, HOST, static_cast<uint16_t>(Ports::SENSORSPORT)) == 1) return 1;

  client -> println(header);
  client -> println(body);
  client -> println();
  client -> stop();

  //body.remove();
  //header.remove();
  return 0;
  
}

/**
 * Send Image buffer to HOST on specified PORT.
*/
int sendImage(WiFiClientSecure *client, camera_fb_t *fb, IPAddress HOST, String timestamp) {
  
  String header = generateHeader(MIMEType::IMAGE_JPG, fb -> len, HOST, WiFi.macAddress(), timestamp);
  if (header == "None") return 1;

  debugln(header);
  debugln();

  if (connect(client, HOST, static_cast<uint16_t>(Ports::IMAGEPORT)) == 1) return 1;

  client -> println(header);
  client -> write(fb -> buf, fb -> len);
  client -> println();
  client -> stop();
  //header.remove();
  return 0;
}

/**
 * Generate a header for a given HTTPS packet.
 */
String generateHeader(MIMEType type, int bodyLength, IPAddress HOST, String macAddress, String timestamp) {

  String mimeType = MIMEStr[static_cast<int>(type)];

  int end = strlen("\r\n");

  int headerLength = HeaderStr[0].length() + end +
                     HeaderStr[1].length() + HOST.toString().length() + end +
                     HeaderStr[2].length() + mimeType.length() + end + 
                     HeaderStr[3].length() + end + 
                     HeaderStr[4].length() + String(bodyLength).length() + end +
                     HeaderStr[5].length() + macAddress.length() + end +
                     HeaderStr[6].length() + timestamp.length();


  String header;
  header.reserve(headerLength+1);

  header += HeaderStr[0]+"\r\n";
  header += HeaderStr[1] + HOST.toString() + "\r\n";
  header += HeaderStr[2] + mimeType +"\r\n";
  header += HeaderStr[3] + "\r\n";
  header += HeaderStr[4] + String(bodyLength) + "\r\n";
  header += HeaderStr[5] + macAddress + "\r\n";
  header += HeaderStr[6] + timestamp + "\r\n";
  
  return header;
}

/**
 * Generate a header for a given HTTPS packet.
 * Some functions return size_t and therefore must be converted.
 * size_t can overflow int as its larger, but we only have 12MB of RAM, and the max image res
 * is like 720p.
 */
String generateHeader(MIMEType type, size_t bodyLength, IPAddress HOST, String macAddress, String timestamp) {
  int length = static_cast<int>(bodyLength);
  return generateHeader(type, length, HOST, macAddress, timestamp);
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
  return String(timestamp);
}


/**
 * Read the SSL certificate for a given network into a char array.  
 */
void readCertificateFile(fs::FS &fs, const char *certPath, const char* &certContent) {

  String pathStr = String(CERT_FOLDER)+"/"+String(certPath);
  File certFile = fs.open(pathStr.c_str());
  if (!certFile) {
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
      debugln("Failed to open config file");
      return false;
  }

  while (file.available()) {
      String line = file.readStringUntil('\n');
      line.trim();

      if (line.startsWith("HOST")) {
          network.HOST.fromString(line.substring(line.indexOf('=') + 1).c_str());
      } else if (line.startsWith("CERT")) {
          String certFileName = line.substring(line.indexOf('=') + 2).c_str(); // Get everything after the '='
          String certFilePath = String(CERT_FOLDER) + "/" + certFileName;  // Adjust the path accordingly
          readCertificateFile(fs, certFilePath.c_str(), network.CERT);
      }
  }

  file.close();
  return true;
}


/**
 * Try to load the config file for a network AP.
 */
bool readAPConf(fs::FS &fs, const char *path, Network &network) {
  String pathStr = String(AP_FOLDER)+"/"+String(path);
  File file = fs.open(pathStr.c_str());
  if (!file) {
      debugln("Failed to open config file");
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
bool readProfile(fs::FS &fs, const char *path, Network &network) {
  String pathStr = String(PROFILE_FOLDER)+"/"+String(path);
  File file = fs.open(pathStr.c_str());
  if (!file) {
    debugln("Failed to open config file");
    return false;
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
  return true;
}

/**
 * Update the firmware for the device.
 */
void OTAUpdate(Network network, String firmware_version) {
  t_httpUpdate_return ret = httpUpdate.update(*network.CLIENT, network.HOST.toString(),
                            static_cast<uint16_t>(Ports::READINGPORT), "/", firmware_version); 
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