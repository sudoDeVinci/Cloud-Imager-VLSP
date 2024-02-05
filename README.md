# Cost-Focused Weather Tracking
### (Cloud Categorization & Tracking)  

- By: Tadj Cazaubon (tc222gf)

## TLDR;
Quick yet accurate Weather prediction is imperative for certain industries to now only survive, but simply exist. An important factor of these is the ability to track, categorize and predict movements of clouds within a given area. Current data is not meant for real-time application on a local area level. The  proposal is the construction of a number of 'weather stations' which take atmospheric readings and images of the sky above them to accurately track cloud cover.

## Background
More location-accurate, real-time weather tracking and prediction is an endeavor with wide-reaching application. These include:
The ability of the average person to better prepare for local weather conditions in their day-today.
More refined weather condition description, such as duration and area of effect for storage units and warehouses.
The ability for solar panel owners to more accurately estimate power output using knowledge of cloud-cover.

These sorts of forecasts are usually made using satellite data. This would be from sources such as the MISR Level 2 Cloud product from NASA, showing cloud-motion vectors accurate to 17.6km [2], or the EUMETSAT MTG 3rd Gen. satellite array with a purported resolution of approx. 1km. [10] This data cannot be used for local weather forecasting however, as cloud-cover obscures the view of the land, as well as cloud-heights and environmental readings for overcast areas being unknowable. 

Cloud-height, visibility, humidity are usually measured on the ground via devices such as ceilometers. This however costs an average of approx. USD $ 30,000 [3] and covers approximately 8 km^2 [12]. Ground-based techniques which utilize a visual component usually do so via the use of calibrated camera arrays performing triangulation (B.Lyu, Y.Chen et al 2021)[13], sometimes going further to separate cloud fields from the sky background to describe cloud cover in terms of both horizontal size and velocity vectors(P.Crispel, G.Roberts 2018)[14]. Techniques which do not make use of a visual component utilize environmental readings such as dewpoint and relative humidity to then calculate the Lifted Condensation Level (LCL). This is “the height at which an air parcel would saturate if lifted adiabatically” [9] and can be used as a stand-in for the base-height of a cloud in a given area. This approach may be able to rival ceilometers in accuracy of +-5m depending on the sensor accuracy [9]. 

 A hybrid approach of 3D approximation of cloud positions may be possible with ‘lower-end’ consumer hardware through determination of cloud height via the LCL. 3D reconstruction through camera calibration via the intrinsic/extrinsic distortion matrices are not novel concepts. Many popular image and computer-vision libraries such as OpenCV have methods for finding these properties [15]. The use of a single fixed-point sky-imager to accurately describe the height, position, and velocity vectors of clouds however, is novel.
Implementation of IoT weather stations which transmit sensor data and sky images over either GSM or Wi-Fi to a central server as well is not novel, being done in (Puja Sharma, Shiva Prakash, 2021). The density of information gathered from a single image at hobbyist cost however, is. The ability to geo-reference ground-based sky images with less data than multi-camera techniques:
Enables systems hobbyists to create and use more accurate weather data.
Generates a higher density of data per unit cost in deployment of IoT weather monitoring systems on a local level. 

## Related work
Finding cloud height and positional data through sky imaging is done usually with multi-camera arrays via triangulation [13][14]. In B.Lyu, Y.Chen et al 2021 [13], the main output is multiple cloud height points. Separation of cloud areas from sky is not done, unlike in P.Crispel & G.Roberts 2018 [14] where cloud area separation is done through visible spectrum filtering, similar to Long et al [22], however, using HSV rather than RGB. We similarly propose obtaining cloud height, however, with only a singular camera, and finding a singular cloud base height value directly above the sensor rather than multiple, using atmospheric calculations to derive cloud height estimates as in  Romps, D. 2017 [9]. Unlike those mentioned however, this height estimate is used by us in obtaining cloud size through 3D reconstruction, rather than through the scale-invariant feature transform (SIFT) used in B.Lyu, Y.Chen et al 2021 [13] and P.Crispel & G.Roberts 2018 [14].  We also propose finding cloud ‘pixels’ in sky images with an approach similar to Long et al [22], filtering by the color ratio of pixel groups, though we propose using multiple color spectrums rather than just RGB; namely RGB, HSV and YCbCr, as well as more modern image pre and post-processing techniques. The cost associated with sky imagers has always been high, though there have been attempts in the past to create inexpensive, miniaturized solutions. Dev et al [23] is a popular example, with Jain et al [5][24] dropping costs further in the area of US$300 per unit capturing 4k images using consumer hardware and compact, 3D printed materials. Our solution drops this cost further, though using 1080p images, whilst retaining the small stature. 

## Proposal
Both a miniaturization and hybridization of existing techniques of cloud feature description must take place. There now exist ceilometer weather stations with reasonable accuracy such as the MWS-M625 from Intellisense which measures at 19 x 14 x 14 cm fitting many high precision instruments, including a 360 deg high-resolution sky imager [20]. Though inexpensive solutions have been shown such as Dev et al [23] in 2016 in creating whole-sky imagers which cost US$2,500 per unit, as well as Jain et al [5][24] in 2021 and 2022 respectively with costs close to US$300, we believe it possible to drop this further, whilst using less data than either.

The lack of hybridization in related works means that the density of information per image is more sparse than possible if a combination of environmental and visual methods are used.
We propose to: 

- [x] Create weather station(s) able to collect and send weather data within expected sensor accuracy.
- [x] Create/host a server which is able to accept multiple connections from these stations and process and store the incoming data.
- [x] Undistort the sky images. This is done by obtaining the intrinsic and extrinsic matrices of the stations prior to their deployment. 
- [ ] Calculate the LCL (Lifted Condensation Level) via the environmental readings given, according to the method outlined in Romps. D (2017).
- [ ] Identify the clouds in the scene via either statistical analysis or simple object detection. 
    
    a. This also then allows identification of the size of the cloud given the focal length and FOV of the camera module.
    
    - [ ] Set up a weather station at the Växjö Kronoberg Airport.

- [ ] Compare the accuracy of the readings, as well as cloud heights against the data of the Växjö Airport. These are available via the METAR Api, and viewable at https://metar-taf.com/ESMX.

## Setup

### ESP32-S3
An Esp32-S3 with an OV5640 DVP camera module is pointed at the sky at a location and predetermined angle (prefereably perpendicular).

1. An SHT31-D takes Relative Humidity and Temperature readings.
2. A BMP390 takes Air Pressure readings.
3. The Dewpoint is calculated according using the Magnus-Tetens formula [8].
4. An image of the sky is taken with the OV5640.
5. The image and readings are sent to a collections server for analysis.


## How

### ESP32-S3

The ESP32-S3-OTG Dev board by Freenove was chosen because of:
1. Better vector instructions for image handling.
2. Insanely better power efficiency.
3. Increased flash memory.
4. OTG capability.

Microcontrollers are programmed using Arduino Studio.
I mostly use VScode for programming. 

* Earlier within the project I used either McroPython and Python for all components. I languages switched due to speed, memory and compatibility concerns.

The [Falsk server](src/Server/server.py), [DB ORM](src/Server/db/) and and [analysis tools](src/Server/analysis/) are written in python for ease of use. 

#### Reading from sensors
To read from the SHT31-D, we use the [Adafruit_SHT31](https://github.com/adafruit/Adafruit_SHT31) library. 
To read from the BMP390, we use the [Adafruit_BMP3XX](https://github.com/adafruit/Adafruit_BMP3XX) libray.
We will be connecting these on the same serial bus to the esp, as they occupy different addresses (0x44 and 0x77 respectively). We use pins not occupied by the cameras on internal serial operations (41 and 42). We use the Wire library to make an instance with these as our SDA and SCL for Serial Bus 0.

* Remember to have 3.3kΩ pull-up resistors (at least 2KΩ seems to work fine).

To make things easier, I store pointers to alot of my sensors and networking related objects in structs. I imagine this helps access times as these are stored in continguous memory, acting as sort of jump tables.

<br>

Sensor state object defined in sensors.h:

```cpp
struct Sensors {
    TwoWire *wire;
    Adafruit_BMP3XX BMP;
    Adafruit_SHT31 SHT;
    camera_fb_t *CAM;

    struct Status {
        bool CAM = false;
        bool SHT = false;
        bool BMP = false;
        bool WIFI = false;
    } status;
};
```

<br>

Network profile object defined in comm.h:

```cpp
struct Network {
    const char* SSID;
    const char* PASS;
    const char* CERT;
    IPAddress HOST;
    IPAddress GATEWAY;
    IPAddress DNS;
    HTTPClient *HTTP;
    WiFiClient *CLIENT;
    tm TIMEINFO;
    time_t NOW;

    /**
     * MIME types for the different types of packets.
     */
    struct MIMEType {
        const String IMAGE_JPG = "image/jpeg";
        const String APP_FORM = "application/x-www-form-urlencoded";
    } mimetypes;

    /**
     * Routes on the Server. 
     */
    struct Route {
        const char* IMAGE = "/images";
        const char* REGISTER = "/register";
        const char* READING = "/reading";
        const char* STATUS = "/status";
        const char* UPDATE = "/update";
        const char* UPGRADE = "/upgrade";
        const char* TEST = "/test";
    } routes;

    struct Header {
        const String CONTENT_TYPE = "Content-Type";
        const String MAC_ADDRESS = "MAC-Address";
        const String TIMESTAMP = "timestamp"; 
    } headers;
};
```

<br>

I use pointers so that I can have a majority of these functions in separate cpp files to separate responsibility. Sensor related functionality is in [sensors.cpp](src/Server/onboard/sensors.cpp), and networking related functionality is in [comm.cpp](src/Server/onboard/comm.cpp). 
Pointers are also useful so that the structures containing them can be kept within a global scope, but mutated within methods. I find this helps keep memory management simple. 

<br>

### Sending Sensor Data

Statuses, readings and images are sent via different functions in comm.cpp. The layout of each function is the same. The readings and statuses are both sent in the URL of GET requests. Once that's sent, we print the return code and end the connection. Low-level details are taken care of by the HTTPClient library.

```cpp
void sendStats(Network *network, Sensors::Status *stat, const String& timestamp) {
    const String PATH = String(network->routes.STATUS);
    IPAddress host = network->HOST;
    
    const String values = "sht="  + String(stat -> SHT) +
                          "&bmp=" + String(stat -> BMP) +
                          "&cam=" + String(stat -> CAM);

    network -> HTTP -> begin(host.toString(), static_cast<int>(Ports::DEFAULT), String(PATH + "?" + values));
    send(network, timestamp);
    network -> HTTP -> end();
}
```

Headers are modified within the send() function in comm.cpp. Both readings and statuses are sent this way.
```cpp
void send(Network *network, const String& timestamp) {
    network -> HTTP -> setConnectTimeout(READ_TIMEOUT);
    network -> HTTP -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.APP_FORM);
    network -> HTTP -> addHeader(network -> headers.MAC_ADDRESS, WiFi.macAddress());
    network -> HTTP -> addHeader(network -> headers.TIMESTAMP, timestamp);

    int httpCode = network -> HTTP -> GET();

    getResponse(network -> HTTP, httpCode); 
}
```

This function is overloaded to send the image buffer from the camera as a POST request.
```cpp
void send(Network *network, const String& timestamp, camera_fb_t *fb) {
    ...
    network -> HTTP -> addHeader(network -> headers.CONTENT_TYPE, network -> mimetypes.IMAGE_JPG);
    ...
    int httpCode = network -> HTTP -> POST(fb -> buf, fb -> len);
    ...  
}
```

## Analysis

Images samples have been taken with both an OV2640 and an OV5640. These are compared with multiple shots from various DSLR cameras, taken as frames from timelapses.  

#### OV5640
Not Yet Available.
<br>

#### OV2460
While colour space based operations are fairly easy on high quality images, the OV2460 is not high quality. Contrast is low, over/under-exposure are almost ensured and ISO changes are not only drastic but cause unwanted light filtering and other strange behaviour:

<img src = 'images/reference_ov2640/Image20.png' alt="Example OV2640 Image" style="height: 300px; width:400px;"/>

### Colourspace Frequency Histogram

First is graphing the frequencies of the BGR and HSV values for clouds versus the sky surrounding them. This is done in [colour_graphs](colour_graphs.py).
Each reference image in [Reference-Images](Reference-Images/) has a corresponding image in [Blocked-Images](Blocked-Images/).

Reference Image            |  Blocked Image
:-------------------------:|:-------------------------:
![Reference Image](images/reference_dslr/Image17.png)  |  ![Blocked Image](images/blocked_dslr/Image17.png)

The Blocked out images are coloured such that clouds are coloured red and the sky is coloured black. Small borders around clouds are left as to not capture the noise of whispy cloud edges.
This is used to create two binary images and subsequent masked images of the reference image, one for the clouds and one for the sky in the scene. These are split, iterated over and their colour values recorded. These values are then graphed and can viewed below.
NOTE: The divisons in the bar graphs is an artifact from saving the graphs as pngs, as the pdf versions do not contain these.

#### Frequency Chart for High Res Images
<br>

These show the frequency graphs for the colour channels of the 60 images of the sky, separated into regions of sky and cloud.

DSLR BGR Bar Graph            |  DSLR HSV Bar Graph
:-------------------------:|:-------------------------:
![Reference Image](Graphs/hist/dslr/new_hist_dslr_RGB.png)  |  ![Blocked Image](Graphs/hist/dslr/new_hist_dslr_HSV.png)

<br>

Above we that viusally, the distributions for these images could be approximated to either normal or beta distributions if properly cleaned, especially that of the clouds.
It is also apparent that the Red and Green colour space would be more useful in the pursuit to classify data.

Above we see that for the most part, only the Saturation channel would be useful for separation/classification, but that the separation between them is more prominent than in other colour channels.

#### Frequency Chart for OV2640
<br>

These show the frequency graphs for the colour channels of the 20 images of the sky taken with the OV2640, separated into regions of sky and cloud. 

OV2640 BGR Bar Graph            |  OV2640 HSV Bar Graph
:-------------------------:|:-------------------------:
![Reference Image](Graphs/hist/ov2640/new_hist_ov2640_RGB.png)  |  ![Blocked Image](Graphs//hist/ov2640/new_hist_ov2640_HSV.png)

<br>

Above we see that while the pattern of separation in the channels in followed, the lack of colour fidelity causes the sky regions to a more bimodal distribution. This can be seen in images where the sky looks more purple than blue, or regions of it are under/overexposed, or subject to strange tinting.

We see that the hue looks somewhat similar, the saturation and value are nothing like the higher resolution images. I attribute this to the camera querks mentioned before. The value distribution for both clouds and sky regions is completely different now, with the sky region peaking at 100, rather than closer to 150 and skewing right.

### ScreePlot
<br>

Once the percentage variance of each colour channel in differentiating cloud and sky pixels is found, these can be visualized as a ScreePlot. This is done within [pca_graphs](pca_graphs.py).

#### ScreePlot for High Res Images
<br>

These show the screeplots for the colour channels of the 60 higher resolution images of the sky, colour channels separated as principle components to check the variance percentage in differentiating sky versus cloud pixels.

**[CURRENTLY UNLABELLED.]**

DSLR BGR Scree Plot            |  DSLR HSV Scree Plot
:-------------------------:|:-------------------------:
![Reference Image](Graphs/PCA/dslr/new_scree_dslr_RGB.png)  |  ![Blocked Image](Graphs/PCA/dslr/new_scree_dslr_HSV.png)

<br>

Above we see that the red channel accounts for ~80% of the variance in the cloud vs sky regions, with the green channel accounting for just under 20%. This means that in classification, the red and green channels are the main factors. We could then discard  

Above we see that the Value channel as expected leads in variance, though the next two channels are closer than one might think when looking at the distribution graphs. Still, the variance of the Value channel alone is almost as much as the other two channels combined (~50%). 

#### ScreePlots for OV2640
<br>

These show the screeplots for the colour channels of the 20 images of the sky taken with the OV2640, colour channels separated as principle components to check the variance percentage in differentiating sky versus cloud pixels.

OV2640 BGR Scree Plot            |  OV2640 HSV Scree Plot
:-------------------------:|:-------------------------:
![Reference Image](Graphs/PCA/ov2640/new_scree_ov2640_RGB.png)  |  ![Blocked Image](Graphs/PCA/ov2640/new_scree_ov2640_HSV.png)

<br>

Above we see that the screeplot for the BGR channels is similar to that of that higher resolution images, despite the lack of image fidelity.

Above we see that there is an even smaller difference between the respective channels, meaning that using them to differentiate the two data sets is more difficult. The channel variance percents do however follow the expected scale.

### PCA ScatterPlot
<br>

Once a matrix of principle components (colour channels) and their per variance values is obtained, these can be visulaized in a PCA Plot. The Data is split into two (cloud pixel variance and sky pixel variance matrices respectively) to allow for better labelling. The two highest variance PCs are then graphed onto a Principle component scatterplot of sky versus cloud pixels. This is the second part of [pca_graphs](pca_graphs.py).

#### PCA ScatterPlot for High Res Images
<br>

DSLR PCA BGR ScatterPlot            |  DSLR PCA HSV Scatterplot
:-------------------------:|:-------------------------:
![BGR PCA ScatterPlot for High Res Images](Graphs/PCA/dslr/new_pca_dslr_RGB.png "BGR PCA ScatterPlot for High Res Images")  |  ![HSV PCA ScatterPlot for High Res Images](Graphs/PCA/dslr/new_pca_dslr_HSV.png "HSV PCA ScatterPlot for High Res Images")

#### PCA ScatterPlot for OV2640
<br>

OV2640 PCA BGR ScatterPlot            |  OV2640 PCA HSV Scatterplot
:-------------------------:|:-------------------------:
![BGR PCA ScatterPlot for ov2640](Graphs/PCA/ov2640/new_pca_ov2640_RGB.png "BGR PCA ScatterPlot for ov2640")  |  ![HSV PCA ScatterPlot for ov2640](Graphs/PCA/ov2640/new_pca_ov2640_HSV.png "HSV PCA ScatterPlot for ov2640")


### Final Comments

- It can be seen that sky and cloud regions can be separated somewhat via visible colour space, and this separation simplified via singular value decomposition. The OV2640 however, can be seen to not be suitable for this application however; though following the statistical trends of the higher resolution images, it lacks the image quality/colour fidelity needed for this application.

[1] The National Oceanic and Atmospheric Administration. 16 November 2012. p. 60.

[2] MISR 17.6 KM GRIDDED CLOUD MOTION VECTORS: OVERVIEW AND ASSESSMENT, Jet Propulsion Laboratory, 4800 Oak Grove, Pasadena, California, K. Mueller, M. Garay, C. Moroney, V. Jovanovic (2012).

[3]  Ceilometer-Based Rain-Rate Estimation: A Case-Study Comparison With S-Band Radar and Disdrometer Retrievals in the Context of VORTEX-SE, F .Rocadenbosch, R. Barragán , S.J. Frasier ,J. Waldinger, D.D. Turner , R.L. Tanamachi, D.T. Dawson (2020) Available: here (Accessed May 19, 2023)

[4] “Misr: Spatial resolution,” NASA, Available: here (Accessed May 19, 2023).

[5] An Extremely-Low Cost Ground-Based Whole Sky Imager, Jain, Mayank & Gollini, Isabella & Bertolotto, Michela & McArdle, Gavin & Dev, Soumyabrata. July 2021. Available: here

[6] A Simplified Analytical Method to Calculate the Lifting Condensation Level from a Skew-T Log-P Chart. Avances en Ciencias e Ingenieria. 7. C124-C129 (Extras), Muñoz, Erith & Mundaray, Rafael & Falcon, Nelson, 2015.

[7] Wmo, “Cumulonimbus,” International Cloud Atlas. Available: here (accessed May 21, 2023)

[8] The Relationship between Relative Humidity and the Dewpoint Temperature in Moist Air: A Simple Conversion and Applications. Bulletin of the American Meteorological Society 86(2) pp. 225-234, Lawrence, M. (2005). Available at: here (Accessed 5 Sep 2023)

[9] Exact Expression for the Lifting Condensation Level. Journal of the Atmospheric Sciences 74(12) pp. 3891-3900, Romps, D. (2017). Available: here (Accessed 26 Jan 2024). 

[10] Meteosat Third Generation, EUMETSTAT, Jan 2021, Available: here

[11] The SEVIRI Instrument, J. Schmid, January 2000, Available: here

[12] CL31 Ceilometer for Cloud Height Detection, Vaisala, 2009 Available: here

[13] Estimating Geo‐Referenced Cloud‐Base Height With Whole‐Sky Imagers. Earth and Space Science, Lyu, Baolei & Chen, Yang & Guan, Yuqiu & Gao, Tianlei & Liu, Jun. August 2021. Available: here

[14]  All-sky photogrammetry techniques to georeference a cloud field. Atmospheric Measurement Techniques, Crispel, Pierre & Roberts, Gregory , January 2018. Available: here

[15] Camera Calibration and 3D Reconstruction, OpenCV - Open Source Computer Vision, 31 Jan 2024. Available: here

[16] DIY Weather Station With ESP32, AutoDesk Instructables, Giovanni Aggiustatutto, Available:  here

[17] ESP32 Weather Station with Weather Forecast, Wireless Sensors and Air Quality Measurement, Harald Kreuzer, 29 June 2023, Available: here

[18] Create A Simple ESP32 Weather Station With BME280, LastMinuteEngineers, Available: here

[19] Complete DIY Raspberry Pi Weather Station With Software, AutoDesk Instructables, spacemanlabs, Available: here

[20] MWS-M625,  Intellisense Systems, Inc, 21041 S. Western Ave, Torrance, CA 90501. Available: here

[21] Real Time Weather Monitoring using IoT, Puja Sharma, Shiva Prakash, ITM Web of Conferences 40(3):01006, August 2021, Available: here

[22]  Retrieving Cloud Characteristics from Ground-Based Daytime Color All-Sky Images. Journal of Atmospheric and Oceanic Technology, Long, Charles & Sabburg, J. & Calbó, Josep & Pages, David. (2006). - J ATMOS OCEAN TECHNOL. 23. 10.1175/JTECH1875.1.
Available: here

[23]  WAHRSIS: A low-cost high-resolution whole sky imager with near-infrared capabilities. Proceedings of SPIE - The International Society for Optical Engineering, Dev, Soumyabrata & Savoy, Florian & Lee, Yee Hui & Winkler, Stefan. May 2014, Available: here

[24] LAMSkyCam: A Low-cost and Miniature Ground-based Sky Camera. HardwareX, Jain, Mayank & Sengar, Vishal & Gollini, Isabella & Bertolotto, Michela & McArdle, Gavin & Dev, Soumyabrata. August 2022 Available: here