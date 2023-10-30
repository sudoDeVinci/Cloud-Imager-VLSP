#include "comm.h"

/**
 * Connect to a HTTPS server.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, IPAddress PORT) {
  int conn_count = 0;
  Serial.print("Connecting to Status Server Socket.");
  while (! client.connect(HOST, PORT)) {
    delay(random(200, 501));
    Serial.print(".");
    conn_count+=1;
    if (conn_count >= 10) {
        Serial.println("Could not connect to server status socket.");
        return 1;
    }
  }
  Serial.println("");
  Serial.println("Connected with client status socket.");
  return 0;
}

/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(WiFiClientSecure *client, char* SSID, char* PASS) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASS);
  WiFi.setSleep(false);
  Serial.print("Connecting to WiFi Network .");
  Serial.print(Network::SSID);
  int connect_count = 0; 
  while (WiFi.status() != WL_CONNECTED) {
      delay(random(400, 601));
      Serial.print(".");
      connect_count+=1;
      if (connect_count >= 10) {
          Serial.println("Could not connect to WIfi.");
          return 1;
      }
  }
  client.setInsecure();
}

/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
int sendReadings(float* readings, int length, IPAddress HOST, IPAddress READINGPORT) {

  String readingStrings[length];
  for(int x = 0; x < length; x++) {
    readingStrings[x] = String(readings[x]);
  }

  String body = "temperature=" + readingStrings[0] + ""\
                "&humidity=" + readingStrings[1] + ""\
                "&pressure=" + readingStrings[2] + ""\
                "&dewpoint=" + readingStrings[3] + "\r\n";

  String header = generateHeader(body.length(), HOST, WiFi.macAddress());
  if (header == "None") return 1;

  Serial.println(header);
  Serial.println(body);
  Serial.println();

  if (connect(HOST, READINGPORT) == 1) return 1;

  client.println(header);
  client.println(body);
  client.println();
  client.stop();
  return 0;
}


/**
 * Send statuses of weather sensors to HOST on specified PORT. 
 */
int sendStatuses(bool* statuses, int length, IPAddress HOST, IPAddress SENSORSPORT) {
  /*
   * Populate the String fields for the POST.
   * We need the stauses for the rest of the program but dont wanna hold a bunch of strings
   * in memory, so we hold them as booleans then convert them to String equivalents before sending.
   */
  String statusStrings[length];
  for(int x = 0; x < length; x++) {
    statusStrings[x] = (statuses[x] ? "true" : "false");
  }

  String body = "sht="  + statusStrings[0] + ""\
                "&bmp=" + statusStrings[1] + ""\
                "&cam=" + statusStrings[2] + "\r\n";

  String header = generateHeader(body.length(), HOST, WiFi.macAddress());
  if (header == "None") return 1;

  Serial.println(header);
  Serial.println(body);
  Serial.println();

  if (connect(HOST, SENSORSPORT) == 1) return 1;

  client.println(packet);
  client.println(body);
  client.println();
  client.stop();
  return 0;
  
}

/**
 * Send Image buffer to HOST on specified PORT.
*/
int sendImage(camera_fb_t *fb, IPAddress HOST, IPAddress IMAGEPORT) {
  
  String header = generateHeader(length, HOST, WiFi.macAddress());
  if (header == "None") return 1;

  Serial.println(header);
  Serial.println();

  if (connect(HOST, IMAGEPORT) == 1) return 1;

  client.println(header);
  client.write(fb -> buf, length);
  client.println();
  client.stop();
  return 0;
}


/**
 * Generate a header for a given HTTPS packet.
 */
String body generateHeader(int bodyLength, IPAddress HOST, String macAddress) {
  /**
   * Get the current time and format the timestamp as MySQL DATETIME.
   * timeinfo is an empty struct whihc is filled by calling getLocalTime().
   */
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return "None";
  }
  char timestamp[20];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);
  String stamp = String(timestamp);

  String header = "POST / HTTP/1.1\r\n"\
                  "Host: " + HOST.toString() + "\r\n"\
                  "Content-Type: application/x-www-form-urlencoded\r\n"\
                  "Connection: close\r\n"\
                  "Content-Length: " + String(bodyLength) + "\r\n"\
                  "MAC-address: " + macAddress + "\r\n";
                  "Timestamp: " + stamp + "\r\n";
  return header;
}

/**
 * Generate a header for a given HTTPS packet.
 * Some functions return size_t and therefore must be converted.
 * size_t can overflow int as its larger, but we only have 12MB of RAM, and the max image res
 * is like 720p.
 */
String body generateHeader(size_t bodyLength, IPAddress HOST, String macAddress) {
  int length = static_cast<int>(bodyLength);
  return generateHeader(int length, IPAddress HOST, String macAddress);
}