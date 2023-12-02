#include "sensors.h"
#include "camera_pins.h"

/**
 * Clock speeds for different camera 
*/

#define MAGNUS_A 17.625
#define MAGNUS_B 243.04
/** 
 * https://metar-taf.com/ESMX
 */
#define SEALEVELPRESSURE_HPA (1020.6)
#define CAMERA_CLK 20000000
#define CAMERA_MODEL_ESP32S3_EYE

#define UNDEFINED -69420.00

/**
 * Setup the SHT31-D and return the sensor object.
 */
void shtSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_SHT31 *sht) {
  if (!sht -> begin()) {
    stat -> SHT = false;
    debugln("Couldn't find SHT31");
  } else {
    stat -> SHT = true;
    debugln("SHT31 found!");
  }
}

/*
 * Setup and calibrate the BMP390. Return the sensor object.
 */
void bmpSetup(TwoWire *wire, Sensors::Status *stat, Adafruit_BMP3XX *bmp) {
  
  if (!bmp -> begin_I2C(0x77, wire)) {
    stat -> BMP = false;
    debugln("Could not find a valid BMP3 sensor, check wiring!");
  } else {
    stat -> BMP = true;
    debugln("BMP found!");
    /**
     * Set up oversampling and filter initialization
     */
    bmp -> setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
    bmp -> setPressureOversampling(BMP3_OVERSAMPLING_4X);
    bmp -> setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
    bmp -> setOutputDataRate(BMP3_ODR_50_HZ);
  }
}

/**
 * Scan Serial connection on predefined pins for sensors. Print the addresses in hex. 
 */
void Scan (TwoWire *wire) {
  debugln ();
  debugln ("I2C scanner. Scanning ...");
  byte count = 0;

  for (byte i = 8; i < 120; i++) {
    wire -> beginTransmission(i);
    if (wire -> endTransmission() == 0) {
      debug ("Found address: ");
      debug (i, DEC);
      debug (" (0x");
      debug (i, HEX);     
      debugln (")");
      count++;
    }
  }
  debug ("Found ");      
  debug (count, DEC);
  debugln (" device(s).");
}

/**
 * Set up camera for taking periodic images.
 * Return 1 if good, 0 if failed at some point. 
 */
void cameraSetup(Sensors::Status *stat) {

  debugln("Setting up camera...");

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
    debugf("Camera init failed with error 0x%x", err);
    stat -> CAM = false;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  s->set_vflip(s, 1); // flip it back
  s->set_brightness(s, 1); // up the brightness just a bit
  s->set_saturation(s, 0); // lower the saturation
  
  debugln("Camera configuration complete!");
  stat -> CAM = true;
}


/**
 * Read the humidity from the SHT-31D in rel percent. Return a String.
 */
void read(Adafruit_SHT31 *sht, float *hum) {
  float h = sht -> readHumidity();
  if(!isnan(h)) *hum = h; 
}

/**
 * Read the Temperature and pressure from the BMP390 in deg C and hPa.
 */
void read(Adafruit_BMP3XX *bmp, double *out) {

  if (! bmp -> performReading()) {
    debugln("Couldn't perform reading in bmp!");
    return;
  }
  double temp = bmp -> temperature;
  if(!isnan(temp)) out[0] = temp;

  double pres = bmp -> pressure;
  if(!isnan(pres)) out[1] = pres;

  float alt = bmp -> readAltitude(SEALEVELPRESSURE_HPA);
  double altitude = static_cast<double>(alt);
  if(!isnan(altitude)) out[2] = altitude;

  return;
}

String calcDP(double temperature, float humidity, double pressure, double altitude) {
    double alpha = ((MAGNUS_A * temperature) / (MAGNUS_B + temperature)) + log(humidity / 100.0);
    double dewPoint = (MAGNUS_B * alpha) / (MAGNUS_A - alpha);

    // Correct for altitude
    dewPoint = dewPoint - (altitude / 1000.0);

    return String(dewPoint);
}

String* readAll(Sensors::Status *stat, Adafruit_SHT31 *sht, Adafruit_BMP3XX *bmp) {
  String* thpd = new String[4]{"None", "None", "None", "None"};
  double* tpa = new double[3]{UNDEFINED, UNDEFINED, UNDEFINED};
  float humidity = UNDEFINED;

  //debugln("Reading from bmp.");
  if(stat -> BMP == true) read(bmp, tpa);
  //debugln("Reading from SHT");
  if(stat -> SHT == true) read(sht, &humidity);

  //debugln("Getting dewpoint");
  if(tpa[0]!=UNDEFINED && tpa[1]!=UNDEFINED && tpa[2]!=UNDEFINED && humidity!=UNDEFINED) {
    String dew = calcDP(tpa[0], humidity, tpa[1], tpa[2]);
    thpd[3] = dew;
  }

  //debugln("Stringifying");
  if(tpa[0] != UNDEFINED) thpd[0] = String(tpa[0]);
  if(humidity != UNDEFINED) thpd[1] = String(humidity);
  if(tpa[1] != UNDEFINED) thpd[2] = String(tpa[1]);
  //debugln("Clearing");

  //debugln("Cleared");
  return thpd;
}

/**
 * Print the readings for the sesnsors.
 */
void printReadings(String* readings) {
  debug(readings[0] + " deg C | ");
  debug(readings[1] + " % | ");
  debug(readings[2] + " hPa | ");
  debug(readings[3] + " deg C | ");
  debugln();
}