#include "comm.h"

#define FIRMWARE_VERSION "0.0.3.0"

TwoWire wire = TwoWire(0);

// Struct holding sensor object pointers and statuses.
Sensors sensors;

// Struct of network information.
NetworkInfo network;

// BMP sensor object.
Adafruit_BMP3XX bmp;

// SHT sensor object.
Adafruit_SHT31 sht;

// SSD1306 i2c OLED object.
Adafruit_SSD1306 display;

void setup() {

    if (DEBUG == 1) { 
      Serial.begin(115200);
      debugln();
      debugln("Setting up...");
    }

    sdmmcInit();

    SEALEVELPRESSURE_HPA = 1012;

    /**
    * wire.begin(sda, scl)
    * 32,33 for ESP32 "S1" WROVER
    * 41,42 for ESP32 S3
    */
    sensors.wire = &wire;
    sensors.wire -> begin(41,42);

    // Connect to wifi and set up the NTP server.
    wifiSetup(&network, &sensors.status);
    configTime(0, 0, "pool.ntp.org");
    setenv("TZ", "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00", 1);  

    // Set up the display.
    display = Adafruit_SSD1306(DISPLAY_WIDTH, DISPLAY_HEIGHT, sensors.wire, -1);
    sensors.SCREEN = display;
    displaySetup(&sensors.status, &sensors.SCREEN);

    // Set up the SHT31-D.
    sht = Adafruit_SHT31(sensors.wire);
    sensors.SHT = sht;
    shtSetup(&sensors.status, &sensors.SHT);

    // Set up the BMP380.
    sensors.BMP = bmp;
    bmpSetup(sensors.wire, &sensors.status, &sensors.BMP);

    // Set up the OV5640.
    cameraSetup(&sensors.status);
    debugln();
}

void loop () {
  resetDisplay(&sensors.SCREEN);

  // Show the sensor statuses.
  displayStatuses(&sensors.status, &sensors.SCREEN, network.SSID);

  // Instantiate the Wifi Client.
  WiFiClientSecure *client = new WiFiClientSecure;
  network.CLIENT = client;

  //SEALEVELPRESSURE_HPA = parseQNH(getQNH(&network));
  debug("QNH: ");
  debug(String(SEALEVELPRESSURE_HPA));
  debugln(" hPa");

  // Read sensor readings into singular Reading object - Display them to the screen.
  Reading currentReading = readAll(&sensors.status, &sensors.SHT, &sensors.BMP);
  currentReading.timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);
  displayReadings(&currentReading, &sensors.SCREEN);

  // Check if there is a connection to the internet.
  if (!sensors.status.WIFI) {
    debugln("NO CONNECTION!  ->  Going to sleep!...");
    delay(50);
    deepSleepMins(20);
  }

  // Attempting to scope the http client to keep it alive in relation to the wifi client.
  {
    HTTPClient https;

    // Check if the site is reachable.
    if (websiteReachable(&https, &network, currentReading.timestamp)) {
      // No need to communicate anymore.
      delete client;

      // Save the readings to the SD Card in CSV format.
      String message = readingsToString(&currentReading);
      debugln(message);
      debugln("\n[WRITING READINGS TO LOG]");
      writeToCSV(SD_MMC, LOG_FILE, message);

      // Refresh the image buffer - Take multiple images.
      if(sensors.status.CAM) {
        camera_fb_t* fb = NULL;
        for(int i = 0; i < 3; i++) {
          fb = esp_camera_fb_get();
          esp_camera_fb_return(fb);
          delay(50);
        }
        fb = esp_camera_fb_get();

        String ts = currentReading.timestamp;
        ts.replace(" ","-");
        ts.replace(":","-");
        String imagePathString = "/" + ts + ".jpg";
        debugln("\n[SAVING IMAGE TO FILE]");
        writejpg(SD_MMC, imagePathString.c_str(), fb -> buf, fb -> len);
        esp_camera_fb_return(fb);
        esp_err_t deinitErr = cameraTeardown();
        if (deinitErr != ESP_OK) debugf("Camera de-init failed with error 0x%x", deinitErr);
      }

      debugln("WEBSITE UNREACHABLE!  ->  Going to sleep!...");
      delay(50);
      deepSleepMins(20);
    }

    /** Update the firmware if possible.
    OTAUpdate(&network, FIRMWARE_VERSION);

    // Send the sensor statuses to server.
    sendStats(&https, &network, &sensors.status, currentReading.timestamp);
    delay(50);

    // Send the current reading to the server.
    sendReadings(&https, &network, &currentReading);
    delay(50);

    // Refresh the image buffer - Take multiple images.
    if(sensors.status.CAM) {
      camera_fb_t * fb = NULL;
      for(int i = 0; i < 3; i++) {
        fb = esp_camera_fb_get();
        esp_camera_fb_return(fb);
        delay(50);
      }
      fb = esp_camera_fb_get();
      
      // Send the image to the server.
      sendImage(&https, &network, fb -> buf, fb -> len, currentReading.timestamp);
      delay(50);
      esp_camera_fb_return(fb);
      esp_err_t deinitErr = cameraTeardown();
      if (deinitErr != ESP_OK) debugf("Camera de-init failed with error 0x%x", deinitErr);
    }

    
    // Read the file content as a vector of strings - Convert to array of readings. 
    std::vector<String*> fileContent = readCSV(SD_MMC, LOG_FILE);
    Reading* loggedReadings = csvToReadings(fileContent);
    
    uint8_t* img;
    
    for (int i = 0; i < fileContent.size(); i ++) {
      printReadings(&loggedReadings[i]);
      String ts = loggedReadings[i].timestamp;
      ts.replace(" ","-");
      ts.replace(":","-");
      String imagePathString = "/" + ts + ".jpg";
      uint8_t* img = readjpg(SD_MMC, imagePathString.c_str());
      size_t len = sizeof(img);
      sendReadings(&https, &network, &loggedReadings[i]);
      sendImage(&https, &network, img, len, loggedReadings[i].timestamp);
    }
    
    delete[] loggedReadings;
    fileContent.clear();
    delete[] img;
    SD_MMC.remove(LOG_FILE);
    delete client;
    */
  }

  delay(50);
  deepSleepMins(20);
}