#include "esp_camera.h"
#include <WiFi.h>
//#include <ArduinoWebsockets.h>
#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"
#define CANON_NAME "esp1"

/*  ===========================
    Enter your WiFi credentials
    =========================== */
const char* ssid = "iPhone 13 mini";
const char* password = "cccccccc";
const char* host = "172.20.10.2";
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

/**
 * 
 */
void loop () {
  size_t imgSize = getImageBuffersize();
  String size = String("[" + String(imgSize) + "]");

  String packet = String(size+"#["+CANON_NAME+"]#[Temperature]#[Humidity]#[Pressure]#[Dewpoint]XX");
  String padded_data = leftpad_str(packet, 64, 'X');

  /**
   * Send sensor data and image size.
   */
  // Print data to serial
  Serial.print("Sending: ");
  Serial.println(padded_data);

  // Send data with buffer headers
  client.println(padded_data);
  delay(500);

  // TODO: Implement ACK ARQ
  
  if (imgSize == 0) {
    Serial.println("Image buffer empty. Only readings sent as-is.");
    delay(500000);
    return;
  }
  // Capture an image multiple times to flush buffer
  camera_fb_t *fb = esp_camera_fb_get();
  esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();
  esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();

  // Send the image buffer
  client.write(fb->buf, imgSize);


  // Free the frame buffer
  esp_camera_fb_return(fb); 
  client.stop();
  delay(500000);
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
char* leftpad_char(const char *input, int totalLength, char paddingChar) {
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

size_t getImageBuffersize(void) {
   camera_fb_t *fb = esp_camera_fb_get(); // Capture an image
    
    if (!fb) {
        Serial.println("Failed to capture image");
        return 0;
    }
    
    size_t imageSize = fb->len; // Get the size of the captured image buffer
    esp_camera_fb_return(fb);   // Return the frame buffer
    Serial.print("Image Buffer Size (bytes): ");
    Serial.println(imageSize);
    return imageSize;
}
