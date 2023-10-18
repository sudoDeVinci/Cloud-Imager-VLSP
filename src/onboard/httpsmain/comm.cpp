#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <Dns.h>


enum Ports: uint16_t {
    READINGPORT = 8080;
    REGISTERPORT = 8081;
    SENSORSPORT = 8082;
    IMAGEPORT = 8083;
}

struct Network {
    const char* SSID;
    const char* PASS;
    const IPAddress HOST;
    const IPAddress GATEWAY;
    const IPAddress DNS;
}



/**
 * Attempt to establish a server connection 10 times.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, uint16_t PORT) {
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
 * Attempt to connect to WiFi 10 times.
 * Return 0 if success, return 1 if not. 
 * 
 */
int wifiSetup(WiFiClientSecure *client) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASS);
  WiFi.setSleep(false);
  Serial.print("Connecting to WiFi Network .");
  Serial.print(SSID);
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
  //client.setCACert(HOMECERT);
  client.setInsecure();
}


/**
 * Send POST Request withn sensor data.
 */
int sendReadings(float* readings, int length) {

  String readingStrings[length];
  for(int x = 0; x < length; x++) {
    readingStrings[x] = String(readings[x]);
  }

  String body = "temperature=" + readingStrings[0] + ""\
                "&humidity=" + readingStrings[1] + ""\
                "&pressure=" + readingStrings[2] + ""\
                "&dewpoint=" + readingStrings[3] + "\r\n";

  String header = "POST / HTTP/1.1\r\n"\
                  "Host: " + HOST.toString() + "\r\n"\
                  "Content-Type: application/x-www-form-urlencoded\r\n"\
                  "Connection: close\r\n"\
                  "Content-Length: " + String(body.length()) + "\r\n"\
                  "MAC-address: " + WiFi.macAddress() + "\r\n";
  

  Serial.println(header);
  Serial.println(body);
  Serial.println();

  if (connect(HOST, READINGPORT) == 1) {
    return 1;
  }
  client.println(header);
  client.println(body);
  return 0;
}

String body generateHeader(IPAddress Host) {

}