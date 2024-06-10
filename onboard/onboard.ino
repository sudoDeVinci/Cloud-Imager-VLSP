#include "comm.h"

#define FIRMWARE_VERSION "0.0.2.0"

/**
 * My beautiful globals
 */
NetworkInfo network;
Adafruit_BMP3XX bmp;
Adafruit_SHT31 sht;
Adafruit_SSD1306 display;
TwoWire wire = TwoWire(0);
Sensors sensors;

 const char* rootCA = R"(
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

void setup() {
  
  if (DEBUG == 1) { 
    Serial.begin(115200);
    debugln();
    debugln("Setting up.");
  }

  sdmmcInit();

  SEALEVELPRESSURE_HPA = UNDEFINED;

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
  network.HOST = "https://devinci.cloud";
  network.SSID = "VLSP-Innovation";
  network.PASS = "9a5mPA8bU64!";
  network.CERT = rootCA;
 
  wifiSetup(network.SSID, network.PASS, &sensors.status);
  const char* ntpServer = "pool.ntp.org";
  const char* timezone = "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00";
  configTime(0, 0, ntpServer);
  setenv("TZ", timezone, 1);  

  display = Adafruit_SSD1306(DISPLAY_WIDTH, DISPLAY_HEIGHT, sensors.wire, -1);
  sensors.SCREEN = display;
  displaySetup(&sensors.status, &sensors.SCREEN);
  
  sht = Adafruit_SHT31(sensors.wire);
  sensors.SHT = sht;
  shtSetup(&sensors.status, &sensors.SHT);

  sensors.BMP = bmp;
  bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);

  cameraSetup(&sensors.status);
}




void loop() {
  resetDisplay(&sensors.SCREEN);

  // Show the sensor statuses.
  displayStatuses(&sensors.status, &sensors.SCREEN, network.SSID);

  // Read sensor readings into singular Reading object - Display them to the screen.
  Reading currentReading = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  currentReading.timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);
  displayReadings(&currentReading, &sensors.SCREEN);

  // Connect to the Wi-Fi.
  WiFiClientSecure *client = new WiFiClientSecure;

  if (client && sensors.status.WIFI) {

    // Get the QNH from the weather server.
    String qnhResponse = getQNH(&network);
    float qnh = parseQNH(qnhResponse);
    

    // Set the certificate to communicate.
    client -> setCACert(rootCA);
    network.CLIENT = client;


    // Attempting to scope the http client to keep it alive in relation to the wifi client.
    {
      // Check for firmware update.
      HTTPClient https;

      // Check if the site is reachable.
      if (websiteReachable(&https, &network, currentReading.timestamp)) {
        
        // Update the firmware if possible.
        OTAUpdate(&network, FIRMWARE_VERSION);

        // Send the sensor statuses to server.
        sendStats(&https, &network, &sensors.status, currentReading.timestamp);
        delay(50);

        /** 
         * Read the file content as a vector of strings - Convert to array of readings. 
         *
         * std::vector<String*> fileContent = readFile(SD_MMC, "/readings.txt");
         * Reading* loggedReadings = csvToReadings(fileContent);
         *
         * uint8_t* img;
         *
         * for (int i = 0; i < fileContent.size(); i ++) {
         *    printReadings(&loggedReadings[i]);
         *    String imagePathString = "/" + loggedReadings[i].timestamp + ".jpg";
         *    uint8_t* img = readjpg(SD_MMC, imagePathString.c_str());
         *    size_t len = sizeof(img);
         *    sendReadings(&https, &network, &loggedReadings[i]);
         *    sendImage(&https, &network, img, len, timestamp);
         * }
         *
         * delete[] loggedReadings;
         * fileContent.clear();
         * delete[] img;
         */

        // Send the current reading to the server.
        sendReadings(&https, &network, &currentReading);
        delay(50);

        /**
         * Refresh the image buffer - Take multiple images.
         */
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
          
          // Send the image to the server.
          sendImage(&https, &network, fb -> buf, fb -> len, currentReading.timestamp);
          delay(50);
          esp_camera_fb_return(fb);
          esp_err_t deinitErr = cameraTeardown();
          if (deinitErr != ESP_OK) debugf("Camera de-init failed with error 0x%x", deinitErr);
        
        }
        
      } else {
        // Save the readings to the SD Card in CSV format.
        String message = readingsToString(&currentReading);
        debugln(message);
        writeToFile(SD_MMC, "/readings.txt", message);

        /**
         * Refresh the image buffer - Take multiple images.
         */
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
          

          String imagePathString = "/" + currentReading.timestamp + ".jpg";
          writejpg(SD_MMC, imagePathString.c_str(), fb -> buf, fb -> len);
          esp_camera_fb_return(fb);
          esp_err_t deinitErr = cameraTeardown();
          if (deinitErr != ESP_OK) debugf("Camera de-init failed with error 0x%x", deinitErr);
        }
      }
    }
  } else {
    debug("No Connection Present.");
  }

  delete client; 

  debugln("Going to sleep!...");
  delay(50);
  deepSleepMins(20);
}