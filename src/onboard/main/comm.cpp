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
    Serial.print(".");
    delay(150);
  } while (((millis() - start) <= (1000 * timer)) && (timeinfo -> tm_year <= 1970));
  Serial.println();
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
      Serial.println("Failed to open config file");
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
      Serial.println("Failed to open config file");
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
    Serial.println("Failed to open config file");
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
      Serial.printf("HTTP_UPDATE_FAILED Error (%d): %s\n", httpUpdate.getLastError(), httpUpdate.getLastErrorString().c_str());
      break;

    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("HTTP_UPDATE_NO_UPDATES");
      break;

    case HTTP_UPDATE_OK:
      Serial.println("HTTP_UPDATE_OK");
      break;
  }
}