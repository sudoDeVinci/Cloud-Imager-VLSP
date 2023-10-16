#include "esp_camera.h"
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
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

/** ===========================
 *  Enter your WiFi credentials
 *  =========================== 
 *  
 *  Should almost definitely store these on disk but here we are.
 */
const char* SSID = "Asimov-2.4GHZ";
const char* PASS = "Asimov42";
const IPAddress HOST(192, 168, 0, 104);

const uint16_t READINGPORT = 8080;
const uint16_t REGISTERPORT = 8081;
const uint16_t SENSORSPORT = 8082;
const uint16_t IMAGEPORT = 8083;
WiFiClientSecure client;


/**
 * Boolean array of sensor statuses 
 * [SHT] || [BMP] || [CAM]
 */
bool STATUSES[] = {false, false, false};

/*
 * Serial for sensors & HTTP client
 */
TwoWire wire = TwoWire(0);

/**
 * Sensor objects to use later 
 */
Adafruit_BMP3XX bmpGlob;
Adafruit_SHT31 shtGlob;


/**
 * Server certificate for testing
 */
const char* TESTCERT  = "-----BEGIN CERTIFICATE-----\n" \
"MIID5TCCAs0CFEr1LysJrhEHEDLyyOLr56g9RNHJMA0GCSqGSIb3DQEBCwUAMIGu\n" \
"MQswCQYDVQQGEwJTRTEYMBYGA1UECAwPS1Jyb25vYmVyZ3MgTGFuMQ4wDAYDVQQH\n" \
"DAVWYXhqbzEbMBkGA1UECgwSTGlubmUgU2NpZW5jZSBQYXJrMRcwFQYDVQQLDA5J\n" \
"bm5vdmF0aW9uIExhYjEVMBMGA1UEAwwMMTkyLjE2OC44Ljk5MSgwJgYJKoZIhvcN\n" \
"AQkBFhl0YWRqLmQuY2F6YXVib25AZ21haWwuY29tMB4XDTIzMTAxMTE0MDkwOVoX\n" \
"DTI0MTAxMDE0MDkwOVowga4xCzAJBgNVBAYTAlNFMRgwFgYDVQQIDA9LUnJvbm9i\n" \
"ZXJncyBMYW4xDjAMBgNVBAcMBVZheGpvMRswGQYDVQQKDBJMaW5uZSBTY2llbmNl\n" \
"IFBhcmsxFzAVBgNVBAsMDklubm92YXRpb24gTGFiMRUwEwYDVQQDDAwxOTIuMTY4\n" \
"LjguOTkxKDAmBgkqhkiG9w0BCQEWGXRhZGouZC5jYXphdWJvbkBnbWFpbC5jb20w\n" \
"ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC6mo5QHIFpniO19igzqMYA\n" \
"yhkKTIOY9Mp5i+7u0WXREu2xWkYN9qocWRRMi6MwI7N+FXAzMaw87npF/s/3eDkk\n" \
"cn4Z17yUcIJHBvV25ig3NnXbbne39jtpaECKPqjznPoPsfTcNdGf5q7apHexgaZZ\n" \
"Y+gkBu892eRHb3iUUQAvKfrbQEbeLsYB+jOVaG1Kf0vfh8e9mKBr38pcRUyDE8ak\n" \
"gQ1PAP8UZziyM8QthyoYQVLD3WGmuV5b03daRtpMHd9oXb5fP38wNuU54XicQv/I\n" \
"XbDnq2lCUpKWCLCSV+xj6LTwsLwiZwAn39dGeUcl1HQ2waMC7Nbujmfqf7teqHb1\n" \
"AgMBAAEwDQYJKoZIhvcNAQELBQADggEBAIRxiWM3VwEYcF0TIB/1RgX3ye77ndGK\n" \
"4P/qVporIqFCytjxP/1zSo+M+1ONqJ2Skc1RESXUN7Z/StrrpR3mqkqIWCfjXrLc\n" \
"6oI7W3PTfR/AnRrKxBnGqyTOiAKbPqThm1WtLUslsZttj4TF2+wqoTkhOjPjj2V1\n" \
"iApUHk4bowLn9cA74c+S/Zydo5Mv8d/go6dypr14pQheYnYjhYdHlUIHSl02aCkK\n" \
"yVXT5AbtDI8oeJryPDSbml2geGVuZ1fHpLEVbX6WC/yh99lUzW4MvDRrSVGQmRBG\n" \
"AfWSbZeM3MycahDxvfOVHYAmXjYTFrSeAaCBEjWB4Bs3IFpXaYJOLaw=\n" \
"-----END CERTIFICATE-----\n";

const char* HOMECERT = "-----BEGIN CERTIFICATE-----\n" \
"MIIDtDCCApygAwIBAgIEZS0cNjANBgkqhkiG9w0BAQsFADCBmzELMAkGA1UEBhMC\n" \
"U0UxEDAOBgNVBAgMB1bDpHhqw7YxFzAVBgNVBAcMDktyb25vYmVyZ3MgTGFuMRcw\n" \
"FQYDVQQKDA5Jbm5vdmF0aW9uIExhYjEjMCEGA1UECwwaVsOkeGrDtiBMaW5uZSBT\n" \
"Y2llbmNlIFBhcmsxIzAhBgNVBAMMGlbDpHhqw7YgTGlubmUgU2NpZW5jZSBQYXJr\n" \
"MB4XDTIzMTAxNjExMTkxOFoXDTI0MTAxNTExMTkxOFowgZsxCzAJBgNVBAYTAlNF\n" \
"MRAwDgYDVQQIDAdWw6R4asO2MRcwFQYDVQQHDA5Lcm9ub2JlcmdzIExhbjEXMBUG\n" \
"A1UECgwOSW5ub3ZhdGlvbiBMYWIxIzAhBgNVBAsMGlbDpHhqw7YgTGlubmUgU2Np\n" \
"ZW5jZSBQYXJrMSMwIQYDVQQDDBpWw6R4asO2IExpbm5lIFNjaWVuY2UgUGFyazCC\n" \
"ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOmPRgG5VT38HxMl1cGOWthe\n" \
"yvX+/CBR1Eby9gw4pa/pmcBsmTCMHS4tSUJ7FBoxpo9SAEYibwqbUSUxW+AxD31L\n" \
"r1qRWLI/eVgum1XZq0DKmBy9B+4DV3o31RAcd0Z+/YmSg+1BnqldZMNoXR3kTRJG\n" \
"WZAH2utiOXeuTLwXmlbKfo/pPtjWMH2qw3zx52HjoagsLkJOsmPZmUXLXrSw/0lT\n" \
"FQ5rVkeAnXeqHJhwQQ5j+8jHyD3UfSIafEo/28MtUFfBIdC1vTARk+dvzLBlCnMd\n" \
"6M9fLn7ayDCJKypEI9c2exGI2/R8u+rY9NwOW721UWH2A4JsVFDfsSM3f3mVDnsC\n" \
"AwEAATANBgkqhkiG9w0BAQsFAAOCAQEAKu5Ygv/H7nCIwLOh3MANtjnM/1EjRqit\n" \
"r4f5SYpwOSXd4up/DdHEZkaPI9qFC59kvk3tLO/df9K8lIcgK3Cc4wP+5PRu4w+l\n" \
"4ANBJg2ZrEsTcczSNmpNv4Fuwh/deh4K31pdYKdZuebvcvuvDj0FLD68LnIyHUKR\n" \
"L/SZCQyiPGgJNJRxh2nOD+9NOVm7Mmy5T04o+Z7zMffEZ10GpzdeFQPXsjBR+SfF\n" \
"chqEjejTXO5fioYKZ3+r8dszFyaG9VIK7nG/Ptq8j85HGCdBBFsseh3eL/ctPJJv\n" \
"cH1vJGvHyQqRldaEKHy+ByIfZWirWkOq+6IFGmaPD557iEVFItMHHA==\n" \
"-----END CERTIFICATE-----\n" ;

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
 * Setup the SHT31-D and return the sensor object.
 */
Adafruit_SHT31 shtSetup(TwoWire *wire) {
  Adafruit_SHT31 sht31 = Adafruit_SHT31(wire);
  if (!sht31.begin()) {
    STATUSES[0] = false;
    Serial.println("Couldn't find SHT31");
  } else {
    STATUSES[0] = true;
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
    STATUSES[1] = false;
    Serial.println("Could not find a valid BMP3 sensor, check wiring!");
  } else {
    STATUSES[1] = true;
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
    STATUSES[2] = false;
    return 1;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  s->set_vflip(s, 1); // flip it back
  s->set_brightness(s, 1); // up the brightness just a bit
  s->set_saturation(s, 0); // lower the saturation
  
  Serial.println("Camera configuration complete!");
  STATUSES[2] = true;
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
 * Attempt to establish a server connection 10 times.
 */
int connect(IPAddress HOST, uint16_t PORT) {
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
  // client.setCACert(HOMECERT);
  client.setInsecure();
  

  Serial.println("");
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  return 0;
}


/**
 * Send POST Request withn sensor data.
 */
int sendReadings(float* readings, int length) {

  /*
   * String array to hold the readings of the various sensors.
   */
  String readingStrings[length];

  /*
   * Populate the String fields for the POST.
   */
  for(int x = 0; x < length; x++) {
    readingStrings[x] = String(readings[x]);
    //Serial.println("Element: " + statusStrings[x]);
  }

  /*
   * Formulate the body String of the POST request
   */
  String body = "temperature=" + readingStrings[0] + ""\
                "&humidity=" + readingStrings[1] + ""\
                "&pressure=" + readingStrings[2] + ""\
                "&dewpoint=" + readingStrings[3];

  /*
   * Formulate the header for the POST request.
   */
  String header = "POST / HTTP/1.1\r\n"\
                  "Host: " + HOST.toString() + "\r\n"\
                  "Content-Type: application/x-www-form-urlencoded\r\n"\
                  "Connection: close\r\n"\
                  "Content-Length: " + String(body.length()) + "\r\n"\
                  "MAC-address: " + WiFi.macAddress() + "\r\n\r\n";
  

  Serial.println(header);
  Serial.println(body);

  /*
   * Do a better loop to check if connected.
   */
  if (connect(HOST, READINGPORT) == 1) {
    return 1;
  }
  client.print(header);
  client.print(body);

  // TODO: ADD ACK LISTEN AND REPLAY
  return 0;

}






/**
 * Send a packet containing the statuses of the varous sensors.
 * [MAC] || [SHT] || [BMP] || [CAM]
 */
int sendStatuses(bool* statuses, size_t length) {

  /*
   * String array to hold the statuses of the various sensors.
   */
  String statusStrings[length];

  /*
   * Populate the String fields for the POST.
   * We need the stauses for the rest of the program but dont wanna hold a bunch of strings
   * in memory, so we hold them as booleans then convert them to String equivalents before sending.
   */
  for(int x = 0; x < length; x++) {
    statusStrings[x] = (statuses[x] ? "true" : "false");
    //Serial.println("Element: " + statusStrings[x]);
  }

  /*
   * Formulate the body String of the POST request
   */
  String body = "sht=" + statusStrings[0]+ ""\
                "&bmp=" + statusStrings[1]+ ""\
                "&cam=" + statusStrings[2]+ "\r\n";


  /*
   * Formulate the header for the POST request.
   */
  String packet = "POST / HTTP/1.1\r\n"\
                  "Host: " + HOST.toString() + "\r\n"\
                  "Content-Type: application/x-www-form-urlencoded\r\n"\
                  "Connection: close\r\n"\
                  "Content-Length: " + String(body.length()) + "\r\n"\
                  "MAC-address: " + WiFi.macAddress()+ "\r\n";

  Serial.println(packet);


  /*
   * Do a better loop to check if connected.
   */
  if (connect(HOST, SENSORSPORT) == 1) {
    return 1;
  }
  client.println(packet);
  client.println(body);
  client.println();

  // TODO: ADD ACK LISTEN AND REPLAY
  return 0;
}






int sendImage() {
  /*
   * Capture an image multiple times to flush buffer
   */
  camera_fb_t *fb = esp_camera_fb_get();
  esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();
  esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();

  if(!fb) {return 1;}

  /*
   * Formulate the header for the POST request.
   */
  String header = "POST /" + String(IMAGEPORT) + " HTTP/1.1\r\n"\
                  "Host: " + HOST.toString() + "\r\n"\
                  "Content-Type: image/jpeg\r\n"\
                  "Connection: close\r\n"\
                  "Content-Length: " + String(fb->len) + "\r\n"\
                  "MAC-address: " + WiFi.macAddress() + "\r\n\r\n";

  client.print(header);
  client.write(fb->buf, fb->len); // Send the image data

  // TODO: ADD ACK LISTEN AND REPLAY

  esp_camera_fb_return(fb); // Release the image buffer
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
   * Check for camera init error. 
   */
  cameraSetup();

  /**
   * Check for BMP init error. 
   */
  bmpSetup(&wire);

  /**
   * Check for SHT init error.
   */
  shtSetup(&wire);

  
  if (sendStatuses(STATUSES, sizeof(STATUSES)) == 1) {
    sleep_minutes(10);
    Serial.println("Rebooting...");
    ESP.restart();
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(10); // this speeds up the simulation
}
