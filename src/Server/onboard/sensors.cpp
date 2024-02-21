#include "sensors.h"
#include "camera_pins.h"

/**
 * Sleep for a specified number of minutes. 
 */
void deepSleepMins(float mins) {
  esp_sleep_enable_timer_wakeup(mins*60000000); //10 seconds
  esp_deep_sleep_start();
}

/**
 * Toggle thr heter for the sht31D.
 */
void toggleHeater(Sensors::Status *stat, Adafruit_SHT31 *sht) {
  if(stat -> SHT) sht -> heater(!(sht -> isHeaterEnabled()));
}

/**
 * Setup the SHT31-D and return the sensor object.
 */
void shtSetup(Sensors::Status *stat, Adafruit_SHT31 *sht) {
  if (!sht -> begin()) {
    stat -> SHT = false;
    if (sht -> isHeaterEnabled()) toggleHeater(stat, sht);
    debugln("Couldn't find SHT31");
  } else {
    stat -> SHT = true;
    debugln("SHT31 found!");
  }
}

/**
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
    bmp -> setPressureOversampling(BMP3_OVERSAMPLING_32X);
    bmp -> setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_15);
    bmp -> setOutputDataRate(BMP3_ODR_50_HZ);
  }
}

/**
 * Set up the camera. 
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
  config.frame_size = FRAMESIZE_QHD;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST; // Needs to be "CAMERA_GRAB_LATEST" for camera to capture.
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 1;

  /** if PSRAM keep res and jpeg quality.
   * Limit the frame size & quality when PSRAM is not available
   */
  if(!psramFound()) {
    debugln("Couldn't find PSRAM on the board!");
    config.frame_size = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.jpeg_quality = 30;
  }

  esp_err_t initErr = esp_camera_init(&config);
  if (initErr != ESP_OK) {
    debugf("Camera init failed with error 0x%x", initErr);
    stat -> CAM = false;
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, -1);     // -2 to 2
  s->set_contrast(s, 1);       // -2 to 2
  s->set_saturation(s, 0);     // -2 to 2
  s->set_special_effect(s, 0); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
  s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
  s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
  s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
  s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
  s->set_aec2(s, 0);           // 0 = disable , 1 = enable
  s->set_ae_level(s, 0);       // -2 to 2
  s->set_aec_value(s, 300);    // 0 to 1200
  s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
  s->set_agc_gain(s, 0);       // 0 to 30
  s->set_gainceiling(s, (gainceiling_t)6);  // 0 to 6 (6 from "timelapse" example sjr, OK)
  s->set_bpc(s, 0);            // 0 = disable , 1 = enable
  s->set_wpc(s, 1);            // 0 = disable , 1 = enable
  s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
  s->set_lenc(s, 1);           // 0 = disable , 1 = enable
  s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
  s->set_vflip(s, 0);          // 0 = disable , 1 = enable
  s->set_dcw(s, 1);            // 0 = disable , 1 = enable
  s->set_colorbar(s, 0);       // 0 = disable , 1 = enable

  delay(100);

  /**
   * Attempt to capture an image with the given settings.
   * If no capture, set camera status to false and de-init camera.
   */
  camera_fb_t *fb = NULL;
  fb = esp_camera_fb_get();
  if(!fb) {
    debugln("Camera capture failed");
    stat -> CAM = false;
    esp_err_t deinitErr = cameraTeardown();
    if (deinitErr != ESP_OK) debugf("Camera de-init failed with error 0x%x", deinitErr);
    debugln();
    esp_camera_fb_return(fb);
    return;
  } else {
    esp_camera_fb_return(fb);
  }
  
  debugln("Camera configuration complete!");
  stat -> CAM = true;
}

esp_err_t cameraTeardown() {
    esp_err_t err = ESP_OK;

    // Deinitialize camera
    err = esp_camera_deinit();

    // Display any errors associated with camera deinitialization
    if (err != ESP_OK) {
        debugf("Error deinitializing camera: %s\n", esp_err_to_name(err));
    } else {
        debugf("Camera deinitialized successfully\n");
    }
    debugln();
    return err;
}

/**
 * Read the humidity and temperature from the SHT-31D.
 */
void read(Adafruit_SHT31 *sht, float *out) {
    float h, t;
    for (int s = 0; s < SAMPLES; s++) {
      h = sht -> readHumidity();
      t = sht -> readTemperature();
      delay(50);
    }
    if(!isnan(h)) out[0] = h;
    if(!isnan(t)) out[1] = t;
}

/**
 * Read the pressure and altitude from the BMP390 in and Pa and meters.
 */
void read(Adafruit_BMP3XX *bmp, double *out) {
  double pres;
  float alt;
  double altitude;

  if (! bmp -> performReading()) return;

  for (int s = 0; s < SAMPLES; s++) {
    pres = bmp -> pressure;
    alt = bmp -> readAltitude(SEALEVELPRESSURE_HPA);
    delay(50);
  }

  altitude = static_cast<double>(alt);

  if(!isnan(pres)) out[0] = pres;
  if(!isnan(altitude)) out[1] = altitude;
}

/**
 * Calculate dewpoint corrected for altitude. 
 */
String calcDP(double temperature, float humidity, double pressure, double altitude) {
    double alpha = ((MAGNUS_A * temperature) / (MAGNUS_B + temperature)) + log(humidity / 100.0);
    double dewPoint = (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
    dewPoint = dewPoint - (altitude / 1000.0);
    return String(dewPoint);
}

/**
 * Read all sensors for info as Strings. 
 */
String* readAll(Sensors::Status *stat, Adafruit_SHT31 *sht, Adafruit_BMP3XX *bmp) {
  String* thpd = new String[4]{"None", "None", "None", "None"};
  double* pa = new double[2]{UNDEFINED, UNDEFINED};
  float* ht = new float[2]{UNDEFINED, UNDEFINED};

  if(stat -> BMP == true) read(bmp, pa);
  if(stat -> SHT == true) read(sht, ht);

  if(ht[1]!=UNDEFINED && ht[0]!=UNDEFINED && pa[0]!=UNDEFINED && pa[1]!=UNDEFINED) thpd[3] = calcDP(ht[1], ht[0], pa[0], pa[1]);

  if(ht[1] != UNDEFINED) thpd[0] = ht[1];
  if(ht[0] != UNDEFINED) thpd[1] = ht[0];
  if(pa[0] != UNDEFINED) thpd[2] = pa[0];
  
  return thpd;
}

/**
 * Print the readings for the sesnsors.
 */
void printReadings(String* readings) {
  debug(readings[0] + " deg C | ");
  debug(readings[1] + " % | ");
  debug(readings[2] + " Pa | ");
  debug(readings[3] + " deg C | ");
  debugln();
}