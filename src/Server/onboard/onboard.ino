#include "comm.h"

#define FIRMWARE_VERSION "0.0.2.0"

/**
 * My beautiful globals
 */
Network network;
Adafruit_BMP3XX bmp;
Adafruit_SHT31 sht;
TwoWire wire = TwoWire(0);
Sensors sensors;

 const char*rootCA = R"(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)";

void setClock() {
  configTime(0, 0, "pool.ntp.org");

  Serial.print(F("Waiting for NTP time sync: "));
  time_t nowSecs = time(nullptr);
  while (nowSecs < 8 * 3600 * 2) {
    delay(500);
    Serial.print(F("."));
    yield();
    nowSecs = time(nullptr);
  }

  Serial.println();
  struct tm timeinfo;
  gmtime_r(&nowSecs, &timeinfo);
  Serial.print(F("Current time: "));
  Serial.print(asctime(&timeinfo));
}

void setup() {
  Serial.begin(115200);
  debugln();
  debugln("Setting up.");

  //sdmmcInit();

  /**
   * wire.begin(sda, scl)
   * 32,33 for ESP32 "S1" WROVER
   * 41,42 for ESP32 S3
   */
  sensors.wire = &wire;
  sensors.wire -> begin(41,42);

  /**
   * Read the profile config for the device network struct. 
   */
  //const char* profile = "devinci_cloud.cfg";
  //readProfile(SD_MMC, profile, network);// TODO: do something cause the profile reading failed.
  network.HOST = "https://devinci.cloud";
  network.SSID = "iPhone 13 mini";
  network.PASS = "cccccccc";
  network.CERT = rootCA;

  wifiSetup(network.SSID, network.PASS, &sensors.status);
  const char* ntpServer = "pool.ntp.org";
  const char* timezone = "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00";
  configTime(0, 0, ntpServer);
  setenv("TZ", timezone, 1);

  setClock();  
  
  sht = Adafruit_SHT31(sensors.wire);
  sensors.SHT = sht;
  shtSetup(&sensors.status, &sensors.SHT);
  sensors.BMP = bmp;
  bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);
  cameraSetup(&sensors.status);
}

void loop() {
  WiFiClientSecure *client = new WiFiClientSecure;
  if (client) {
    client -> setCACert(rootCA);
    network.CLIENT = client;
    /*
    Attempting to scope the http client to keep it alive in relation to the wifi client*/
    {
      HTTPClient https;
      //OTAUpdate(&network, FIRMWARE_VERSION);

      String timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);

      debugln("\n[STATUS]");
      const String values ="sht="  + String(stat -> SHT) +
                          "&bmp=" + String(stat -> BMP) +
                          "&cam=" + String(stat -> CAM);

      String url;
      url.reserve(strlen(network.HOST) + strlen(network.routes.STATUS) + values.length() + 2);
      url.concat(network.HOST);
      url.concat(network.routes.STATUS);
      url.concat("?" + values);

      https.begin(*network -> CLIENT, "https://devinci.cloud/api/status?sht=0&bmp=0&cam=0");

      debugln(url);
      int httpCode = https.GET();

        // httpCode will be negative on error
        if (httpCode > 0) {
          // HTTP header has been send and Server response header has been handled
          Serial.printf("[HTTPS] GET... code: %d\n", httpCode);
  
          // file found at server
          if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
            String payload = https.getString();
            Serial.println(payload);
          }
      delay(50);
      https.end();
    }

    delete client;
    
    /**
    String* readings = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
    delay(50);
    printReadings(readings);
    sendReadings(&network, readings, timestamp);
    delete[] readings;
    delay(50);
    
    if(sensors.status.CAM) {
      camera_fb_t * fb = NULL;
      fb = esp_camera_fb_get();
      esp_camera_fb_return(fb);
      delay(50);
      fb = esp_camera_fb_get();
      esp_camera_fb_return(fb);
      delay(50);
      fb = esp_camera_fb_get();
      esp_camera_fb_return(fb);
      delay(50);
      fb = esp_camera_fb_get();
      sendImage(&network, fb, timestamp);
      esp_camera_fb_return(fb);
      delay(50);
      esp_err_t deinitErr = cameraTeardown();
      if (deinitErr != ESP_OK) debugf("Camera init failed with error 0x%x", deinitErr);
    } 
    **/
  }

  debugln("Going to sleep!...");
  delay(50);
  deepSleepMins(10);
}