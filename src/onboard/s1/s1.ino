#include "esp_camera.h"
#include <Arduino.h>
#include <WiFi.h>
#include "Adafruit_SHT31.h"
#include "Adafruit_BMP3XX.h"
#include <Wire.h>

// Select camera model
#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
#include "camera_pins.h"
#define CANON_NAME "Lab000"
#define MAGNUS_A 17.625
#define MAGNUS_B 243.04

// https://metar-taf.com/ESMX
#define SEALEVELPRESSURE_HPA (1020.6)


/*  ===========================
    Enter your WiFi credentials
    =========================== */
const char* ssid = "VLSP-Innovation";
const char* password = "9a5mPA8bU64!";
const char* host = "192.168.8.97";
const uint16_t port = 880;

TwoWire wire = TwoWire(0);
WiFiClient client;

void setup() {

  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up:");
  wire.begin(32,33);

  // Check for camera init error
  cameraSetup();

  // Check for wifi init error
  wifiSetup();
  
  /*
   * Scan the serial connections three times to check connections to devices.
   */
  Scan();
  delay(100);
}

void loop() {

 /*
  * Setup the sensors and return objects to use later.
  */
Adafruit_BMP3XX bmpGlob = bmpSetup(&wire);
Adafruit_SHT31 shtGlob = shtSetup(&wire);

while (1) {
  Serial.println();
  // If bmp not reading, try again in 2 minutes.
  if (! bmpGlob.performReading()) {
    Serial.println("Failed to perform reading :(");
    delay(120000);
    return;
  } else {
    Serial.println("________________________\n");
  }

  /*
   * Get measurements and print them out.
   */
  float humidity = shtGlob.readHumidity();
  float pressure = bmpGlob.readPressure();
  float temperature = bmpGlob.readTemperature();
  float dewpoint = calcDewpoint(temperature, humidity);

  Serial.print("Pressure: "); Serial.print(pressure); Serial.println(" hPa");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  Serial.print("Temperature: "); Serial.print(temperature); Serial.println(" C");
  Serial.print("DewPoint: "); Serial.print(dewpoint); Serial.println(" C");



  // Capture an image multiple times to ensure flushed buffer
  camera_fb_t *fb = esp_camera_fb_get();
  esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();
  esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();

  // Get image buffer size
  size_t imageSize;
  if (!fb) {
    Serial.println("Failed to capture image");
    imageSize = 0;
  } else {
    imageSize = fb->len;
  }
  Serial.print("Image Buffer Size (bytes): ");
  Serial.println(imageSize);

  // Try to connect to our server.
  if (!client.connect(host, port)) {
    Serial.println("Couldn't connect to host.");
    return;
  }
  Serial.println("Successfully connected!");

  /*
   * Construct the packet to be sent.
   */
  String packet = constructPacket(imageSize, temperature, humidity, pressure, dewpoint);
  Serial.println("Packet: " + packet);

  //Send the packet
  client.println(packet);
  delay(1000);
  if (imageSize == 0) {
    Serial.println("Image buffer empty. Only readings sent as-is.");
    delay(500000);
    return;
  }
  // Send the image buffer
  client.write(fb->buf, imageSize);

  // Free the frame buffer
  esp_camera_fb_return(fb); 
  client.stop();
  delay(15000);
}

}

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


/*
 * Setup and calibrate the BMP390. Return the sensor object.
 */
Adafruit_BMP3XX bmpSetup(TwoWire *wire) {
  Adafruit_BMP3XX bmp;
  if (!bmp.begin_I2C(0x77, wire)) {
    Serial.println("Could not find a valid BMP3 sensor, check wiring!");
  } else {
    Serial.println("BMP found!");
    /* 
      * Set up oversampling and filter initialization
      */
    bmp.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
    bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
    bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
    bmp.setOutputDataRate(BMP3_ODR_50_HZ);
  }

  return bmp;
}


/*
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
 * Alpha function for dewpoint calculation. 
 * alpha(T, RH) = ln(RH/100) + aT/(b+T)
 */
float alpha(float T, float RH) {
  return log(RH / 100.0) + (MAGNUS_A * T) / (MAGNUS_B + T);
}

/*
 * https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
 * https://journals.ametsoc.org/view/journals/apme/35/4/1520-0450_1996_035_0601_imfaos_2_0_co_2.xml
 */
float calcDewpoint(float T, float RH) {
  float dew = (MAGNUS_B * alpha(T, RH)) / (MAGNUS_A - alpha(T, RH));
  return dew;
}

/**
 * Attempt to connect to WiFi times.
 * Return 1 if success, return 0 if not. 
 * 
*/
int wifiSetup(void) {
   WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    WiFi.setSleep(false);

    int connect_count = 0; 
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        connect_count+=1;
        if (connect_count >= 10) {
            Serial.println("Could not connect to WIfi.");
            return 0;
        }
    }
    Serial.println("");
    Serial.print("WiFi connected with IP: ");
    Serial.println(WiFi.localIP());
    return 1;
}

/**
 * Set up camera for taking periodic images.
 * Return 1 if good, 0 if failed at some point. 
*/
int cameraSetup(void) {
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
  config.xclk_freq_hz = 12000000;
  config.frame_size = FRAMESIZE_FHD;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 15;
  config.fb_count = 1;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return 0;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  s->set_vflip(s, 1); // flip it back
  s->set_brightness(s, 1); // up the brightness just a bit
  s->set_saturation(s, 0); // lower the saturation
  
  Serial.println("Camera configuration complete!");
  return 1;
}


/*
 * 
 */
String leftpad_str(const String &input, int totalLength, char paddingChar) {
    int inputLength = input.length();
    int outputLength = max(totalLength, inputLength);

    String output;
    output.reserve(outputLength);

    int paddingAmount = outputLength - inputLength;

    for (int i = 0; i < paddingAmount; i++) {
        output += paddingChar;
    }

    output += input; // Append the original string to the padded string
    return output;
}


/*
 * Concatenate the readings into packet structure.
 */
String constructPacket(size_t size, float T, float RH, float Pa, float DP) {
  String packet = "";
  packet.concat("[" + String(size) + "]#");
  packet.concat("[" + String(CANON_NAME) + "]#");
  packet.concat("[" + String(T) + "]#");
  packet.concat("[" + String(RH) + "]#");
  packet.concat("[" + String(Pa) + "]#");
  packet.concat("[" + String(DP) + "]XX");
  return leftpad_str(packet, 64, 'X');
}