# Mesh Network for Cloud Detection, Tracking and Categorization
- By: Tadj Cazaubon (tc222gf)

## Proposal

Quick yet accurate Weather prediction is imperative for certain industries to now only survive,
but simply exist. An important factor of these is the ability to track, categorize and predict
movements of clouds within a given area.

The main tool in determining cloud characteristics is a ceiolmeter, which uses a laser/light source to determine a cloud's base or ceiling height. A Ceilometer usually can also measure aerosol concentration in air [1]. The downside is that ceilometers have a relatively small area of measurement directly
above the unit (~8km2) which would not be an issue, however, as of 2020 they can cost around USD $30 000 per unit [3].
There exists however, high quality satellite data made available by NASA. The new MISR Level 2 Cloud product contains height-resolved, cloud motion vectors at 17.6 km resolution; cloud top heights at 1.1 km resolution; and cross-track cloud motion components at 1.1 km resolution [2]. Now this data is made available to be used by software engineers to visualize as needed. The issue? This data is not meant for real-time application on a local area level. These products are made for global application, collecting data only on the sunlit side of earth over the course of 9 days [4]. A better solution for the local-area level must be thought of then, to better predict cloud movement and category.
<br>
The formal proposal made to VLSP can be viewed in the [Proposal](proposal.pdf)
<br>
Due to the amorphous and feature-sparse nature of Clouds, tracking them via conventional image processing techniques such as via contours, frame-to-frame motion tracking and identifiable features allowing for conventional NN training is surprisingly difficult.
However, I believe:

1. Accurately tracking/identifying clouds may be as simple as identifying them via a statistical analysis of their colour values across multiple colour spaces.

2. Cloud categorization may be done via a combination of atmospheric readings, as well as the colour analysis. 

3. With the cloud base height, location and frame to frame motion of a cloud available to us, we can assign velocity vectors to cloud structures, along with the area of   effect for their shadows on the ground.

<br>

My proposal is the construction of a number of 'weather stations' which take atmospheric readings and images of the sky above them. The data is sent back to a central server and analysed. 

The following is an attempt to put into practice the most current research to create a mesh network of these weather staions which can detect, track, and categorize clouds.


## Setup

An Esp32 (base model or S3) with an OV5640 DVP camera module is pointed at the sky at a location and predetermined angle (prefereably perpendicular).

1. An SHT31-D takes Relative Humidity readings.
2. A BMP390 takes Air Pressure and Temperature readings.
3. The dewpoint is calculated according using the Magnus-Tetens formula [8].
4. An image of the sky is taken.
5. The image and readings are sent to a collections server for analysis.

## How to

Microcontrollers are programmed using Arduino Studio.
I mostly use VScode for programming. 

* Earlier within the project I used either  micropython and python for all components. I languages switched due to speed, memory and compatibility concerns.

[Server components](src/server_components/) are made in Java, and [microcontrollers](src/onboard/) are programmed in C. Graphing components for now are stil made in python for simplicity, but I plan to write these in JavaCV to integrate them within [Server components](src/server_components/).

Sometimes however, I use [adafruit ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy) for interfacing with the boards due to needing more complex operations, such as the [utility](/utility/) scripts. This was mainly used before the switch, but readers may find use in these.
Many of the utility board functions are alternatively available through esp-IDF, but setup and use of it are memory intensive and complex. My development machine (2C4t Celeron J4125 w/ 8GB DDR4) simply cant take it.

### ESP32 WROVER

The ESP32 WROVER Dev board by Freenove was chosen simply because of availability and driver support for the DVP camera.
The manufacturer repository for the board can be found [here](https://github.com/Freenove/Freenove_ESP32_WROVER_Board).

#### Reading from sensors
To read from the SHT31-D, we use the Adafruit_SHT31 library. 
To read from the BMP390, we use the Adafruit_BMP3XX libray.
We will be connecting these on the same serial bus to the esp, as they occupy different addresses (0x44 and 0x77 respectively). We use pins not occupied by the cameras on internal serial operations (32 and 33). We use the Wire library to make an instance with these as our SDA and SCL for Serial Bus 0.

```C
...

TwoWire wire = TwoWire(0);

void setup() {
  Serial.begin(115200);
  wire.begin(32,33);

  ...

}

...
```

I've created an initialization function for each sensor. We pass the reference to the TwoWire instance we create, then attempt to initialize and calibrate them. We then get each of the readings as well as the dewpoint.

```C
...
Adafruit_BMP3XX bmpGlob = bmpSetup(&wire);
Adafruit_SHT31 shtGlob = shtSetup(&wire);

while (true) {
  if (! bmpGlob.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }

  float humidity = shtGlob.readHumidity();
  float pressure = bmpGlob.readPressure();
  float temperature = bmpGlob.readTemperature();
  float dewpoint = calcDewpoint(temperature, humidity);
  ...
}
...
```

When sending the readings, they're made into a string with a psecified format:
```C

...

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
```

leftpad_str() is a leftpad function I made to ensure the packet is always a fixed-size.

#### Taking a picture
Taking a picture with the OV5640 is the same as the OV2640, however the sensor frequency must be changed from 20MHZ to 12MHZ, and the OV5640 allows for up 1080p images comfortably. The ESP32 WROVER has PSRAM, meaning we can use FHD resolutions and a slightly higher jpeg compression quality. Here is the camera setup I used for initializing the OV5640:

```C
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
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 15;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return 0;
  }

  sensor_t * s = esp_camera_sensor_get();
  s->set_vflip(s, 1); // flip it back
  s->set_brightness(s, 1);
  s->set_saturation(s, 0);
  
  Serial.println("Camera configuration complete!");
  return 1;
}
```
If your controller does not have PSRAM, you may want to do another optional check, and lower your settings accordingly.
Simply, to take a picture, and get teh image size in bytes once the camera is initialized:

```C
    #include "esp_camera.h"

    ...

    camera_fb_t *fb = esp_camera_fb_get();
    esp_camera_fb_return(fb);
    fb = esp_camera_fb_get();
    esp_camera_fb_return(fb);
    fb = esp_camera_fb_get();

    size_t imageSize;
    if (!fb) {
        imageSize = 0;
    } else {
        imageSize = fb->len;
    }
    Serial.print("Image Buffer Size (bytes): ");
    Serial.println(imageSize);
```

We need the image size in bytes for sending the data over tcp, and writing it to the jpeg on the server. We flush the buffer mutliple times to ensure the new picture taken is in fact new.

```C
 esp_camera_fb_return(fb)
```
Returns and empties the image buffer.


#### Wi-Fi Connection
Wi-Fi connection is simple so I'll gloss over it. Firstly specify the connection credentials.
```C
const char* ssid = "**************";
const char* password = "*********";
const char* host = "255.255.255.247";
const uint16_t port = 69;
```
Now we attempt to connecto the the Access point a set number of times, each time checking the conection state. very simple but effective way in most cases.
```C
#include <WiFi.h>

... 

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
```

Within our main loop() now, we must:

1. Instantiate a connection with the server:
```C
#include <WiFi.h>

...

WiFiClient client;

...

void loop() {
    ...
    
    if (!client.connect(host, port)) {
        Serial.println("Couldn't connect to host.");
        return;
    }
    Serial.println("Successfully connected!");
    
    ...
}
```

2. Construct and send the packet as a padded string.
```C
    ...

    String packet = constructPacket(imageSize, temperature, humidity, pressure, dewpoint);
    Serial.println("Packet: " + packet);

    client.println(packet);
    delay(1000);

    ...

```

3. If the image buffer is not 0, write it to the server socket.
```C
...

if (imageSize == 0) {
    Serial.println("Image buffer empty. Only readings sent as-is.");
    delay(500000);
    return;
  }

  client.write(fb->buf, imageSize);

  esp_camera_fb_return(fb); 

  ...

```

4. CLose the socket connection.
```C
...

client.stop();

...

```

### Server
TODO: SHOW SERVER IMPLEMENTATION.


## Analysis

### Image Quality Requirements

#### OV5640
Not Yet Available.
<br>

#### OV2460
While colour space based operations are fairly easy on high quality images, the OV2460 is not high quality. Contrast is low, over/under-exposure are almost ensured and ISO changes are not only drastic but cause unwanted light filtering and other strange behaviour:

<img src = 'Reference-Images-esp\Image77.png' alt="MarineGEO circle logo" style="height: 300px; width:400px;"/>

In all, while the camera is not exactly suited for this application, it is what is available and what I was able to test with. The shortcomings become apparent below.

### Colourspace Frequency Histogram

First is graphing the frequencies of the BGR and HSV values for clouds versus the sky surrounding them. This is done in [colour_graphs](colour_graphs.py).
Each reference image in [Reference-Images](Reference-Images/) has a corresponding image in [Blocked-Images](Blocked-Images/).


<img src = 'Reference-Images\Image17.png' alt="MarineGEO circle logo" style="height: 300px; width:400px;"/>
<img src = 'Blocked-Images\Image17.png' alt="MarineGEO circle logo" style="height: 300px; width:400px;"/>

The Blocked out images are coloured such that clouds are coloured red and the sky is coloured black. Small borders around clouds are left as to not capture the noise of whispy cloud edges.
This is used to create two binary images and subsequent masked images of the reference image, one for the clouds and one for the sky in the scene. These are split, iterated over and their colour values recorded. These values are then graphed and can viewed below.
NOTE: The divisons in the bar graphs is an artifact from saving the graphs as pngs, as the pdf versions do not contain these.

#### Frequency Chart for High Res Images
<br>

These show the frequency graphs for the colour channels of the 60 images of the sky, separated into regions of sky and cloud.


<img src = 'Graphs/BGRBarGraph.png' alt="BGR Frequency Chart for High Res Images" style="height: 500px; width:600px;"/>
<img src = 'Graphs/HSVBarGraph.png' alt="HSV Frequency Chart for High Res Images" style="height: 500px; width:600px;"/>

<br>

Above we that viusally, the distributions for these images could be approximated to normal distributions if properly cleaned, especially that of the clouds.
It is also apparent that the Red and Green colour space would be more useful in the pursuit to classify data.

Above we see that for the most part, only the 
Value channel would be useful for separation/classification, but that the separation between them is more prominent than in other colour channels.

#### Frequency Chart for OV2640
<br>

These show the frequency graphs for the colour channels of the 20 images of the sky taken with the OV2640, separated into regions of sky and cloud. 

<img src = 'Graphs/BGRBarGraph-esp.png' alt="BGR Frequency Chart for High Res Images" style="height: 500px; width:600px;"/>
<img src = 'Graphs/HSVBarGraph-esp.png' alt="HSV Frequency Chart for High Res Images" style="height: 500px; width:600px;"/>

<br>

Above we see that while the pattern of separation in the channels in followed, the lack of colour fidelity causes the sky regions to a more bimodal distribution. This can be seen in images where the sky looks more purple than blue, or regions of it are under/overexposed, or subject to strange tinting.

We see that the hue looks somewhat similar, the saturation and value are nothing like the higher resolution images. I attribute this to the camera querks mentioned before. The value distribution for both clouds and sky regions is completely different now, with the sky region peaking at 100, rather than closer to 150 and skewing right.

### ScreePlot
<br>

Once the percentage variance of each colour channel in differentiating cloud and sky pixels is found, these can be visualized as a ScreePlot. This is done within [pca_graphs](pca_graphs.py).

#### ScreePlot for High Res Images
<br>

These show the screeplots for the colour channels of the 60 higher resolution images of the sky, colour channels separated as principle components to check the variance percentage in differentiating sky versus cloud pixels.

<img src = 'Graphs/BGRScree.png' alt="BGR Screeplot for High Res Images" style="height: 500px; width:600px;"/>
<img src = 'Graphs/HSVScree.png' alt="HSV Screeplot for High Res Images" style="height: 500px; width:600px;"/>

<br>

Above we see that the red channel accounts for ~80% of the variance in the cloud vs sky regions, with the green channel accounting for just under 20%. This means that in classification, the red and green channels are the main factors. We could then discard  

Above we see that the Value channel as expected leads in variance, though the next two channels are closer than one might think when looking at the distribution graphs. Still, the variance of the Value channel alone is almost as much as the other two channels combined (~50%). 

#### ScreePlots for OV2640
<br>

These show the screeplots for the colour channels of the 20 images of the sky taken with the OV2640, colour channels separated as principle components to check the variance percentage in differentiating sky versus cloud pixels.

<img src = 'Graphs/BGRScree-esp.png' alt="BGR Screeplot for High Res Images" style="height: 500px; width:600px;"/>
<img src = 'Graphs/HSVScree-esp.png' alt="HSV Screeplot for High Res Images" style="height: 500px; width:600px;"/>

<br>

Above we see that the screeplot for the BGR channels is similar to that of that higher resolution images, despite the lack of image fidelity.

Above we see that there is an even smaller difference between the respective channels, meaning that using them to differentiate the two data sets is more difficult. The channel variance percents do however follow the expected scale.

### PCA ScatterPlot
<br>

Once a matrix of principle components (colour channels) and their per variance values is obtained, these can be visulaized in a PCA Plot. The DataFrame of all pixels is split into two (cloud pixel variance and sky pixel variance dataframes respectively) to allow for better labelling. The two highest variance PCs are then graphed onto a Principle component scatterplot of sky versus cloud pixels. This is the second part of [pca_graphs](pca_graphs.py).

#### PCA ScatterPlot for High Res Images
<br>

![BGR PCA ScatterPlot for High Res Images](/Graphs/BGRPcaGraph.png "BGR PCA ScatterPlot for High Res Images")
![HSV PCA ScatterPlot for High Res Images](/Graphs/HSVPcaGraph.png "HSV PCA ScatterPlot for High Res Images")

#### PCA ScatterPlot for OV2640
<br>

![BGR PCA ScatterPlot for ESPImages](/Graphs/BGRPcaGraph-esp.png "BGR PCA ScatterPlot for ESP Images")
![HSV PCA ScatterPlot for ESP Images](/Graphs/HSVPcaGraph-esp.png "HSV PCA ScatterPlot for ESP Images")

### Final Comments

- It can be seen that sky and cloud regions can be separated somewhat via visible colour space, and this separation simplified via singular value decomposition. The OV2640 however, can be seen to not be suitable for this application however; though following the statistical trends of the higher resolution images, it lacks the image quality/colour fidelity needed for this application.

## References

[1] The National Oceanic and Atmospheric Administration. 16 November 2012. p. 60.

[2] K. Mueller, M. Garay, C. Moroney, V. Jovanovic (2012). MISR 17.6 KM GRIDDED CLOUD
MOTION VECTORS: OVERVIEW AND ASSESSMENT, Jet Propulsion Laboratory, 4800 Oak
Grove, Pasadena, California.

[3] F .Rocadenbosch, R. Barragán , S.J. Frasier ,J. Waldinger, D.D. Turner , R.L. Tanamachi, D.T. Dawson (2020) Ceilometer-Based Rain-Rate Estimation: A Case-Study Comparison With S-Band Radar and Disdrometer Retrievals in the Context of VORTEX-SE

[4] “Misr: Spatial resolution,” NASA, https://misr.jpl.nasa.gov/mission/misr-instrument/spatial-resolution/ (accessed May 19, 2023).

[5] “tlcl_rh_bolton,” Tlcl_rh_bolton,
https://www.ncl.ucar.edu/Document/Functions/Contributed/tlcl_rh_bolton.shtml (accessed May 21, 2023) (Extras)

[6] Muñoz, Erith & Mundaray, Rafael & Falcon, Nelson. (2015). A Simplified Analytical Method to Calculate the Lifting Condensation Level from a Skew-T Log-P Chart. Avances en Ciencias e
Ingenieria. 7. C124-C129 (Extras)

[7] Wmo, “Cumulonimbus,” International Cloud Atlas, https://cloudatlas.wmo.int/en/observation-of-clouds-from-aircraft-descriptions-cumulonimbus.html (accessed May 21, 2023)

[8] Lawrence, M. (2005). The Relationship between Relative Humidity and the Dewpoint Temperature in Moist Air: A Simple Conversion and Applications. Bulletin of the American Meteorological Society 86(2) pp. 225-234. Available at: https://journals.ametsoc.org/view/journals/bams/86/2/bams-86-2-225.xml [Accessed 5 Sep 2023]