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
  Serial.print("Connecting to WiFi Network " + String(SSID));
  int connect_count = 0; 
  while (WiFi.status() != WL_CONNECTED) {
      delay(random(400, 601));
      Serial.print(".");
      connect_count+=1;
      if (connect_count >= 10) {
          Serial.println("Could not connect to Wifi.");
          stat -> WIFI = false;
          return 1;
      }
  }
  stat -> WIFI = true;
  client -> setInsecure();
  Serial.println("Connected!");
  return 0;
}


/**
 * Connect to a HTTPS server.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, uint16_t PORT) {
  int conn_count = 0;
  Serial.print("Connecting to Status Server Socket.");
  while (! client -> connect(HOST, PORT)) {
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
 * Send readings from weather sensors to HOST on specified PORT. 
 */
int sendReadings(WiFiClientSecure *client, String* readings, int length, IPAddress HOST) {

  String body = "temperature=" + readings[0] + ""\
                "&humidity=" + readings[1] + ""\
                "&pressure=" + readings[2] + ""\
                "&dewpoint=" + readings[3] + "\r\n";

  String header = generateHeader(MIMEType::APP_FORM, body.length(), HOST, WiFi.macAddress());
  if (header == "None") return 1;

  Serial.println(header);
  Serial.println(body);
  Serial.println();

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
int sendStatuses(WiFiClientSecure *client, Sensors::Status *stat, IPAddress HOST) {

  String body = "sht="  + String(stat -> SHT) + ""\
                "&bmp=" + String(stat -> BMP) + ""\
                "&cam=" + String(stat -> CAM)+ "\r\n";

  String header = generateHeader(MIMEType::APP_FORM, body.length(), HOST, WiFi.macAddress());
  if (header == "None") return 1;

  Serial.println(header);
  Serial.println(body);
  Serial.println();

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
int sendImage(WiFiClientSecure *client, camera_fb_t *fb, IPAddress HOST) {
  
  String header = generateHeader(MIMEType::IMAGE_JPG, fb -> len, HOST, WiFi.macAddress());
  if (header == "None") return 1;

  Serial.println(header);
  Serial.println();

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
String generateHeader(MIMEType type, int bodyLength, IPAddress HOST, String macAddress) {
  
  String stamp = getTime();
  String mimeType = MIMEStr[static_cast<int>(type)];


  String header = "POST / HTTP/1.1\r\n"\
                  "Host: " + HOST.toString() + "\r\n"\
                  "Content-Type: "+ mimeType +"\r\n"\
                  "Connection: close\r\n"\
                  "Content-Length: " + String(bodyLength) + "\r\n"\
                  "MAC-address: " + macAddress + "\r\n"\
                  "Timestamp: " + stamp + "\r\n";
  return header;
}

/**
 * Generate a header for a given HTTPS packet.
 * Some functions return size_t and therefore must be converted.
 * size_t can overflow int as its larger, but we only have 12MB of RAM, and the max image res
 * is like 720p.
 */
String generateHeader(MIMEType type, size_t bodyLength, IPAddress HOST, String macAddress) {
  int length = static_cast<int>(bodyLength);
  return generateHeader(type, length, HOST, macAddress);
}


/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct whihc is filled by calling getLocalTime().
  */
String getTime() {
  const char* ntpServer = "pool.ntp.org";
  const long  gmtOffset_sec = 1;
  const int   daylightOffset_sec = 3600;
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return "None";
  }
  char timestamp[20];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%d-%H-%M-%S", &timeinfo);
  return String(timestamp);
}