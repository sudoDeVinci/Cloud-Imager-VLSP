#include "esp_camera.h"
#include <WiFi.h>
//#include <ArduinoWebsockets.h>
#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"


/*  ===========================
    Enter your WiFi credentials
    =========================== */
const char* ssid     = "Asimov-2.4GHZ";
const char* password = "Asimov42";
const char* host = "192.168.0.104";
const uint16_t port = 880;


WiFiClient client;
void setup() {
  // Init serial
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  Serial.println();

  // return if camera init error
  if (cameraSetup() == 0) {
    return ;
  }

  // return if wifi init error
  if (wifiSetup() == 0) {
    return;
  }

  if (!client.connect(host, port)) {
    Serial.println("Couldn't connect to host.");
    return;
  }
  Serial.println("Successfully connected!");
  
}

void loop () {
  char data[] = "X[first]|[second]|[third]XXXXX";
  char* padded_data = leftpad(data, 50, 'X');

  Serial.print("Sending: ");
  Serial.println(padded_data);

  client.write((const uint8_t*)padded_data, 50);
  client.stop();
  while(true){}
  return ;

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
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
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
        if (connect_count >= 5) {
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
 * right-pad the existing string with 'X'
*/
char* leftpad(const char *input, int totalLength, char paddingChar) {
    int inputLength = strlen(input);
    int outputLength = max(totalLength, inputLength) + 1; // +1 for null terminator

    char *output = new char[outputLength];
    int paddingAmount = outputLength - inputLength;

    for (int i = 0; i < paddingAmount; i++) {
        output[i] = paddingChar;
    }

    strcpy(output + paddingAmount, input); // Append the original string to the padded string
    return output;
}
