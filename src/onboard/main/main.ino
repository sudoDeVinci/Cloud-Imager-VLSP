#include "esp_camera.h"
#include <Arduino.h>
#include <WiFi.h>
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>


/**
 * Select camera model
 * #define CAMERA_MODEL_WROVER_KIT
 */

#define CAMERA_MODEL_ESP32S3_EYE

/**
 * Clock speeds for different camera 
*/
#define CAMERA_CLK 20000000


#include "camera_pins.h"
#define MAGNUS_A 17.625
#define MAGNUS_B 243.04

/** 
 * https://metar-taf.com/ESMX
 */
#define SEALEVELPRESSURE_HPA (1020.6)

/**
 * Time to sleep 
 */
#define SLEEP_TIME_MINUTES 10 

/**
 * Define OP CODES for various packets being sent. 
 */
#define READING 0x01
#define REGISTER 0x08
#define SENSORS 0x04
#define IMAGE 0x02

/**
 * Byte array of sensor statuses 
 * [0000 0100] || [MAC] || [SHT] || [BMP] || [CAM] ||  [WIFI]
 */
uint8_t STATUSES[11] = {SENSORS, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};


/** ===========================
 *  Enter your WiFi credentials
 *  =========================== 
 *  
 *  Should almost definitely store these on disk but here we are.
 */
const char* SSID = "VLSP-Innovation";
const char* PASS = "9a5mPA8bU64!";
const IPAddress HOST(192, 168, 8, 100);

const uint16_t READINGPORT = 8080;
const uint16_t REGISTERPORT = 8081;
const uint16_t SENSORSPORT = 8082;
const uint16_t IMAGEPORT = 8083;

/*
 * Serial for sensors & HTTP client
 */
TwoWire wire = TwoWire(0);
WiFiClient client;

/**
 * Sensor objects to use later 
 */
Adafruit_BMP3XX bmpGlob;
Adafruit_SHT31 shtGlob;

/**
 * Enter deep sleep for amount of minutes (converted to miocroseconds)
 */
void sleep_minutes(int minutes) {
  #include <esp_sleep.h>
  esp_sleep_enable_timer_wakeup(minutes * 60000000);
  esp_deep_sleep_start();
}

/**
 * Enter deep sleep for amount of minutes (converted to miocroseconds)
 */
void sleep_secs(int secs) {
  #include <esp_sleep.h>
  esp_sleep_enable_timer_wakeup(secs * 1000000);
  esp_deep_sleep_start();
}

/**
 * Attempt to connect to WiFi 10 times.
 * Return 1 if success, return 0 if not. 
 * 
 */
int wifiSetup(void) {
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
  Serial.println("");
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  return 0;
}

/**
 * Setup the SHT31-D and return the sensor object.
 */
Adafruit_SHT31 shtSetup(TwoWire *wire) {
  Adafruit_SHT31 sht31 = Adafruit_SHT31(wire);
  if (!sht31.begin()) {
    Serial.println("Couldn't find SHT31");
  } else {
    Serial.println("SHT31 found!");
  }
  return sht31;
}

/*
 * Setup and calibrate the BMP390. Return the sensor object.
 */
Adafruit_BMP3XX bmpSetup(TwoWire *wire) {
  Adafruit_BMP3XX bmp;
  if (!bmp.begin_I2C(0x77, wire)) {
    Serial.println("Could not find a valid BMP3 sensor, check wiring!");
  } else {
    Serial.println("BMP found!");
    /**
     * Set up oversampling and filter initialization
     */
    bmp.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
    bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
    bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
    bmp.setOutputDataRate(BMP3_ODR_50_HZ);
  }

  return bmp;
}

/**
 * Set up camera for taking periodic images.
 * Return 1 if good, 0 if failed at some point. 
 */
int cameraSetup(void) {

  Serial.println("Setting up camera...");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = CAMERA_CLK;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;


  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  // for larger pre-allocated frame buffer.
  if(psramFound()){
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    // Limit the frame size when PSRAM is not available
    config.frame_size = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return 1;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  s->set_vflip(s, 1); // flip it back
  s->set_brightness(s, 1); // up the brightness just a bit
  s->set_saturation(s, 0); // lower the saturation
  
  Serial.println("Camera configuration complete!");
  return 0;
}

/**
 * Scan Serial connection on predefined pins for sensors. Print the addresses in hex. 
 */
void Scan () {
  Serial.println ();
  Serial.println ("I2C scanner. Scanning ...");
  byte count = 0;

  for (byte i = 8; i < 120; i++) {
    wire.beginTransmission (i);
    if (wire.endTransmission () == 0) {
      Serial.print ("Found address: ");
      Serial.print (i, DEC);
      Serial.print (" (0x");
      Serial.print (i, HEX);     
      Serial.println (")");
      count++;
    }
  }
  Serial.print ("Found ");      
  Serial.print (count, DEC);
  Serial.println (" device(s).");
}

/**
 * Send a status packet. 
 */
int sendStatus(uint8_t* data, size_t length) {

  int conn_count = 0;
  Serial.print("Connecting to Status Server Socket.");
  while (! client.connect(HOST, SENSORSPORT)) {
    delay(random(400, 601));
    Serial.print(".");
    conn_count+=1;
    if (conn_count >= 10) {
        Serial.println("Could not connect to server status socket.");
        return 1;
    }
  }
  Serial.println("");
  Serial.println("Connected with client status socket.");
  Serial.println("Sending status data:");

  for (size_t i = 0; i < length; i++) {
      Serial.print(data[i], HEX);
      Serial.print(" ");
  }

  Serial.println(" ");
  delay(50);
  client.write(data, length);
  delay(50);
  Serial.println("Data sent.");

  Serial.print("Checking connection to Status Server Socket.");

  while (! client.connect(HOST, SENSORSPORT)) {
    delay(random(400, 601));
    Serial.print(".");
    conn_count+=1;
    if (conn_count >= 10) {
        Serial.println("Could not connect to server status socket.");
        return 1;
    }
  }

  Serial.println("");
  Serial.println("Connected with client status socket sustained.");
  return 0;
}

void setup() {

  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up:");

  /**
   * wire.begin(sda, scl)
   * 32,33 for ESP32 WROVER
   * 41,42 for ESP32 S3
   */
  wire.begin(41,42);

  /**
   * Check for wifi init error.
   * If no wifi, attempt to restart object.
   */
  if (wifiSetup() == 1) {
    sleep_minutes(10);
    Serial.println("Rebooting...");
    ESP.restart();
  }

  /**
   * Get MAC address and copy it to the status packet.
   */
  uint8_t MAC[6];
  WiFi.macAddress(MAC);
  for (int i = 0; i < 6; i++) {
    STATUSES[i + 1] = MAC[i];
  }
  Serial.print("MAC: ");
  Serial.print(WiFi.macAddress());
  Serial.println("");

  /**
   * Check for camera init error. 
   */
  if (cameraSetup() == 1) {
    STATUSES[9] = 0xff; 
  }

  /**
   * Check for SHT init error.
   */
  if (isnan(shtSetup(&wire).readHumidity())) {
    STATUSES[7] = 0xff;
  }

  /**
   * Check for BMP init error. 
   */
  if (! bmpSetup(&wire).performReading()) {
    STATUSES[8] = 0xff;
  }

  if (sendStatus(STATUSES, sizeof(STATUSES)) == 1) {
    sleep_minutes(10);
    Serial.println("Rebooting...");
    ESP.restart();
  }
}

void loop(){

  /*
   * Setup the sensors and return objects to use later.
   */
  WiFi.mode(WIFI_OFF);
  btStop();
  sleep_minutes(0.5);
  setup();
}