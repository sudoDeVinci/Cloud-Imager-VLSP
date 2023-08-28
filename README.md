# Cloud Detection via Visual Colour Space: Concept Exploration using the OV2640
- By: Tadj Cazauon (tc222gf)

## Proposal

Quick yet accurate Weather prediction is imperative for certain industries to now only survive,
but simply exist. An important factor of these is the ability to track, categorize and predict
movements of clouds within a given area. Ceilometers use a laser/light source to determine a
cloud's base or ceiling height. A Ceilometer usually can also measure aerosol concentration in
air [1]. The downside is that ceilometers have a relatively small area of measurement directly
above the unit which would not be an issue, however, as of 2020 they can cost around USD
$30 000 per unit [3].
There exists however, high quality satellite data made available by NASA. The new MISR Level
2 Cloud product contains height-resolved, cloud motion vectors at 17.6 km resolution; cloud top
heights at 1.1 km resolution; and cross-track cloud motion components at 1.1 km resolution [2].
Now this data is made available to be used by software engineers to visualize as needed. The
issue? This data is not meant for real-time application on a local area level. These products are
made for global application, collecting data only on the sunlit side of earth over the course of 9
days [4].
A better solution for the local-area level must be thought of then, to better predict cloud
movement and category.

The formal proposal made to VLSP can be viewed in the [Proposal](proposal.pdf)

<br>

Due to the amorphous and feature-sparse nature of Clouds, tracking them via conventional image processing techniques such as via contours, frame-to-frame motion tracking and identifiable features allowing for conventional NN training, they are surprisingly difficult to autonomously track frame-to-frame.
However, accurately tracking clouds may be as simple as identifying them via a statistical analysis of their colour values across multiple colour spaces. While object detection and identification is done via feature detection, usually on highly downscaled greyscale images,
I believe identification of clouds could come down to BGR and HSV values.
With the cloud base height, location and frame to frame motion of a cloud available to us, we can more accurately assign velocity vectors to cloud structures, along with the area of effect for their shadows on the ground.

<br>

The following is an exploration of this concept with a focus on the camera module. 

## Main Issues

The main issues with the implementation of this concept are:
1. Camera fidelity
2. Weather sensor Accuracy


## Setup

An Esp32 with an OV2460 DVP camera module is pointed at the sky at a location and predetermined angle (prefereably perpendicular). A pycom board connects to a web server started on the esp32 and retrieves the image. The pycom board takes a number of measurements of the surroundings including the humidity, temperature, dew point and estimated cloud height. This information, along with the image is then sent back to a server listening for the pycom device.

## How to

All components are programmed using either python or micropython.

I mostly use VScode for programming, however I use Thonny to update and interface with the boards.
Sometimes however, I use [adafruit ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy) for interfacing with the boards due to needing more complex operations, such as the [utility](/utility/) scripts.

### ESP32 WROVER

The ESP32 WROVER by Freenove was chosen simply because of availability and driver support for the DVP camera.
The manufacturer repository for the board can be found [here](https://github.com/Freenove/Freenove_ESP32_WROVER_Board). Flashing the board can be done within minutes using [esptool](https://github.com/espressif/esptool) and the firmware can be found [here](https://github.com/Freenove/Freenove_ESP32_WROVER_Board/tree/main/Python/Python_Firmware).
<br>

Firmware flashing instructions via esptool can be found [here](https://micropython.org/download/esp32/), but the gist is:
1. Install esptool using pip:
```bash
pip install esptool
```

2. Erase the existing flash memory on the chip:
```
esptool.py --chip esp32 --port <PORT> erase_flash
```

3. From then on program the firmware starting at address 0x1000:
```
esptool.py --chip esp32 --port <PORT> --baud 460800 write_flash -z 0x1000 <FIRMWARE .BIN>
```

### Pycom FiPy and PySense

These should work out of the box, but may require additional drivers for the expansion board.

A helpful guide for their installation can be found [here](https://docs.pycom.io/gettingstarted/software/drivers/).

## Usage

Usage can be broken down into the three components of the project, the:
- FiPy board (with pysense expansion board)
- ESP32 camera board
- Home Windows server.

### ESP32 Camera Board

All files meant to be on the esp32 board are within the [esp32 folder](esp32/). [clear_lib](esp32/clear_lib.py) and [update_lib](esp32/update_lib.py) are simple scripts meant to clear and update the on-board lib folder respectively. The [main](esp32/main.py) simply calls [serve_image](esp32/serve_image.py). [serve_image](esp32/serve_image.py):

1. Activates the on-board wifi 
```python
def server_start():
    SSID = "ImageServer"
    PASSWORD = "12345678"
    from network import WLAN, AP_IF
    
    wlan = WLAN(AP_IF)
    wlan.active(True)
    wlan.config(essid = SSID, password = PASSWORD)
    
    conf = wlan.ifconfig()
    print('Connected, IP address:', conf)
    return wlan
```
2. Listens on port 80 for a request to connect.
```python
s = socket()

try:
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        s.bind(('',88))
        s.listen(100)
        send(s)
        # sleep for 1 minute after sending
        sleep(60000)
    except Exception as e:
        print(e, "err")
        if s:
            s.close()
        raise OSError
except Exception as e:
    print(e)
    if s:
        s.close()
    if wlan:
        wlan.disconnect()
```

3. Send the image buffer contents over the socket connection. I have used a helper [Client class](client.py) to simplify the data transfer. The image buffer is rewritten twice to ensure it's flushed.
```python
from socket import socket
def send(s:socket):
    from struct import pack
    from camera import deinit, capture
    
    while True: 
        camera_init()
        c,a = s.accept()
        print('Connection from {0}'.format(a))
        
        buf = capture()
        buf = capture()
        buf = capture()

        length = len(buf)
        data = bytes(buf)
        print("Sending Image data..")
        
        c.send(pack('<I',length))
        c.sendall(data)
        
        print("Image sent.")
        sleep(2)
        del c,a, buf, length
        deinit()
        collect()
```

### FiPy w/ Pysense Board

All files meant to be on the FiPy board are within the [pycom folder](pycom/). [clear_lib](pycom/clear_lib.py) and [update_lib](pycom/update_lib.py) are simple scripts meant to clear and update the on-board lib folder respectively.The [main](pycom/main.py) simply calls the cycle function within [image_transfer](pycom/image_transfer.py). This:

1. Runs a cycle of attempting to connect to the esp32 board
```python
def connect(SSID, PASSWORD, wlan):
    if PASSWORD is None:
        wlan.connect(ssid=SSID)
    else:
        wlan.connect(SSID, auth=(WLAN.WPA2, PASSWORD))
    print('connecting..',end='')
    while not wlan.isconnected():
        sleep(1)
        print('.',end='')
    print('Connected on:', wlan.ifconfig()[0])
    return wlan.ifconfig()[3]
```

2. Receive an image.
```python
def get_image():
    SSID = "ImageServer"
    PASSWORD = None
    wlan = WLAN(mode=WLAN.STA)
    
    ip = connect(SSID,PASSWORD,wlan)
    sleep(1)
    print("Requesting..")
    from client import Listener
    try:
        with Listener(ip, 88) as c:
            print("Receiving..")
            data = c.get()
            if not data:
                print("No Image received")
        wlan.disconnect()
        del wlan, SSID, PASSWORD, c, ip
        print("Received.")
        collect()
        return data
```
3. Take readings
```python
def readings():
    from pysense import pysense
    py = pysense()

    temp = py.temperature()
    humidity = py.humidity()
    altitude = py.altitude()
    dew_point = py.dew_point()
    
    readings = "{0}|{1}|{2}|{3}".format(altitude, temp, humidity, dew_point)

    return bytes(readings.encode('utf-8'))
```
4. Send the image data to the desktop server on a different WiFi network. Images and readings are sent separately.

```python
def send_image(data):
    SSID = "********"         
    PASSWORD = "********"
    wlan = WLAN(mode=WLAN.STA)

    connect(SSID,PASSWORD,wlan)
    
    from socket import socket
    import struct
    sleep(1)
    addr = "********"
    port = 88
    s = socket()
    
    try:
        s.connect((addr,port))
        sleep(1)

        length = len(data)
        print("Sending image data ...")
        s.send(struct.pack('<I',length))
        s.sendall(data)
        print("Sent")
        sleep(2)
        
        r = readings()
        length = len(r)
        print("Sending readings data...")
        s.send(struct.pack('<I',length))
        s.sendall(r)
        sleep(2)
        s.close()
        print("Sent")
        wlan.disconnect()
        del wlan, length, r, s
        collect()

    except Exception as e:
        if wlan:
            wlan.disconnect()
            del wlan
        if s:
            s.close()
        print(e)
        return None
```

### Listener Server

The [Listener.py](listener.py) script contains a simple web socket, listening for connections on port 88. The server in this case is given a static IP for simplicity. 

```python
def main():
    counter = find_count()
    s = socket()
    try:
        # Try to let the socket address be reusable
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            # Try to bind the socket to an address and port
            s.bind(('',88))
            s.listen(100)
            # Listen, looping repeatedly
            listen(s, counter)
        except Exception as e:
            print(e, "err")
    except Exception as e:
        print(e)
        if s:
            s.close()
```

Once a connection is made, the image data is received and saved with a timestamp

```python
c,a = s.accept()
with Listener(c) as l:
    print('Connection from {0}'.format(str(a)))
    
    datestamp = str(datetime.now().strftime("%Y%m%d"))
    filename = f"img{counter}.png"
    folder = datestamp
    if not os.path.exists("espimages/"+folder):
        os.mkdir("espimages/"+folder)

    print("Receiving Image..")

    try:
        data = l.get()
        if not data:
            print("No Image received")
        else:
            print("Received")
            with open("espimages/"+folder+"/"+filename, "wb") as f:
                f.write(data)
    except Exception as e:
        print(e)
```
After this, the readings are received and saved with the same timestamp in .csv format.

```python
 filename = f"readings{datestamp}{counter}.csv"
headers = ["altitude", "temp", "humidity", "dew_point"]

try:
    print("Receiving sensor data..")
    data = l.get()
    if not data:
        print("No Sensor data received")
    else:
        print("Got Readings")
        bytestring = data.decode('utf-8')
        readings = bytestring.split("|")
        print("Received", readings)
        with open("espimages/"+folder+"/"+filename,  'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerow(readings)
except Exception as e:
    print(e, "err")
    if s:
        s.close()
    raise e
```


## Analysis

### Image Quality Requirements
While colour space based operations are fairly easy on high quality images, the OV2460 is not high quality. Contrast is low, over/under-exposure are almost ensured and ISO changes are not only drastic but cause unwanted light filtering and other strange behaviour:

![Example Image](espimages/20220704/img2022070443.png)

In all, while the camera is not exactly suited for this application, it is what is available and what I was able to test with. The shortcomings become apparent below.

### Colourspace Frequency Histogram

First is graphing the frequencies of the BGR and HSV values for clouds versus the sky surrounding them. This is done in [colour_graphs](colour_graphs.py).
Each reference image in [Reference-Images](Reference-Images/) has a corresponding image in [Blocked-Images](Blocked-Images/).

![reference image](Reference-Images/Image17.png)
![blocked image](Blocked-Images/Image17.png)

The Blocked out images are coloured such that clouds are coloured red and the sky is coloured black. Small borders around clouds are left as to not capture the noise of whispy cloud edges.
This is used to create two binary images and subsequent masked images of the reference image, one for the clouds and one for the sky in the scene. These are split, iterated over and their colour values recorded. These values are then graphed and can viewed below.
NOTE: The divisons in the bar graphs is an artifact from saving the graphs as pngs, as the pdf versions do not contain these.

#### Frequency Chart for High Res Images
<br>

These show the frequency graphs for the colour channels of the 60 images of the sky, separated into regions of sky and cloud.

![BGR Frequency Chart for High Res Images](/Graphs/BGRBarGraph.png "BGR Frequency Chart for High Res Images")

Above we that viusally, the distributions for these images could be approximated to normal distributions if properly cleaned, especially that of the clouds.
It is also apparent that the Red and Green colour space would be more useful in the pursuit to classify data.

![HSV Frequency Chart for High Res Images](/Graphs/HSVBarGraph.png "BGR Frequency Chart for High Res Images")

Above we see that for the most part, only the 
Value channel would be useful for separation/classification, but that the separation between them is more prominent than in other colour channels.

#### Frequency Chart for ESP Images
<br>

These show the frequency graphs for the colour channels of the 20 images of the sky taken with the OV2640, separated into regions of sky and cloud. 

![BGR Frequency Chart for ESP Images](/Graphs/BGRBarGraph-esp.png "BGR Frequency Chart for ESP Images")

Above we see that while the pattern of separation in the channels in followed, the lack of colour fidelity causes the sky regions to a more bimodal distribution. This can be seen in images where the sky looks more purple than blue, or regions of it are under/overexposed, or subject to strange tinting.

![HSV Frequency Chart for ESP Images](/Graphs/HSVBarGraph-esp.png "HSV Frequency Chart for ESP Images")

Above we see that the hue looks somewhat similar, the saturation and value are nothing like the higher resolution images. I attribute this to the camera querks mentioned before. The value distribution for both clouds and sky regions is completely different now, with the sky region peaking at 100, rather than closer to 150 and skewing right.

### ScreePlot
<br>

Once the percentage variance of each colour channel in differentiating cloud and sky pixels is found, these can be visualized as a ScreePlot. This is done within [pca_graphs](pca_graphs.py).

#### ScreePlot for High Res Images
<br>

These show the screeplots for the colour channels of the 60 higher resolution images of the sky, colour channels separated as principle components to check the variance percentage in differentiating sky versus cloud pixels.

![BGR ScreePlot for High Res Images](/Graphs/BGRScree.png "BGR ScreePlot for High Res Images")

Above we see that the red channel accounts for ~80% of the variance in the cloud vs sky regions, with the green channel accounting for just under 20%. This means that in classification, the red and green channels are the main factors. We could then discard  

![HSV ScreePlot for High Res Images](/Graphs/HSVScree.png "HSV ScreePlot for High Res Images")

Above we see that the Value channel as expected leads in variance, though the next two channels are closer than one might think when looking at the distribution graphs. Still, the variance of the Value channel alone is almost as much as the other two channels combined (~50%). 

#### ScreePlots for ESPImages
<br>

These show the screeplots for the colour channels of the 20 images of the sky taken with the OV2640, colour channels separated as principle components to check the variance percentage in differentiating sky versus cloud pixels.

![BGR ScreePlot for ESP Images](/Graphs/BGRScree-esp.png "BGR ScreePlot for ESP Images")

Above we see that the screeplot for the BGR channels is similar to that of that higher resolution images, despite the lack of image fidelity.

![HSV ScreePlot for ESP Images](/Graphs/HSVScree-esp.png "HSV ScreePlot for ESP Images")

Above we see that there is an even smaller difference between the respective channels, meaning that using them to differentiate the two data sets is more difficult. The channel variance percents do however follow the expected scale.

### PCA ScatterPlot
<br>

Once a matrix of principle components (colour channels) and their per variance values is obtained, these can be visulaized in a PCA Plot. The DataFrame of all pixels is split into two (cloud pixel variance and sky pixel variance dataframes respectively) to allow for better labelling. The two highest variance PCs are then graphed onto a Principle component scatterplot of sky versus cloud pixels. This is the second part of [pca_graphs](pca_graphs.py).

#### PCA ScatterPlot for High Res Images
<br>

![BGR PCA ScatterPlot for High Res Images](/Graphs/BGRPcaGraph.png "BGR PCA ScatterPlot for High Res Images")
![HSV PCA ScatterPlot for High Res Images](/Graphs/HSVPcaGraph.png "HSV PCA ScatterPlot for High Res Images")

#### PCA ScatterPlot for ESP Images
<br>

![BGR PCA ScatterPlot for ESPImages](/Graphs/BGRPcaGraph-esp.png "BGR PCA ScatterPlot for ESP Images")
![HSV PCA ScatterPlot for ESP Images](/Graphs/HSVPcaGraph-esp.png "HSV PCA ScatterPlot for ESP Images")

### Final Comments

- It can be seen that sky and cloud regions can be separated somewhat via visible colour space, and this separation simplified via singular value decomposition. The OV2640 however, can be seen to not be suitable for this application however; though following the statistical trends of the higher resolution images, it lacks the image quality/colour fidelity needed for this application.

    - In the near future, the OV5640 must be tested, as this seems to be a large step in image quality, with quality of life features lacking in the OB2640, such as dynamically adjustable focus and ISO.

- The communication between the Esp32 and FiPy is unneedingly convoluted. This is mainly because the FiPy requires the Pysense expansion bored for USB UART communication for programming. The pysense extension board lacks any headers for communication over something such as UART.

    - Using the pysense expansion board was due to it having all the necessary sensors for the needed design, being cheaper than buying them separately. However, I have decided to instead use separate, more accurate sensors such as the SHT31-D and BMP390, connecting them over I2C to a single board.

Over the course of the undertaking, the guiding philosophy was to create as close to a final implementation as possible within the time limit, creating many parts simultaneously, including transmission of weather values and camera distortion matrix calibration (available in [Extras](extras.md)). This unfocused approach made it difficult to fully test the capability of the camera to distinguish in cases of darker clouds, or during inconvenient weather conditions such as rain or the sun being in frame.

## References

[1] The National Oceanic and Atmospheric Administration. 16 November 2012. p. 60.

[2] K. Mueller, M. Garay, C. Moroney, V. Jovanovic (2012). MISR 17.6 KM GRIDDED CLOUD
MOTION VECTORS: OVERVIEW AND ASSESSMENT, Jet Propulsion Laboratory, 4800 Oak
Grove, Pasadena, California.

[3] F .Rocadenbosch, R. Barragán , S.J. Frasier ,J. Waldinger, D.D. Turner , R.L. Tanamachi,
D.T. Dawson (2020) Ceilometer-Based Rain-Rate Estimation: A Case-Study Comparison With
S-Band Radar and Disdrometer Retrievals in the Context of VORTEX-SE

[4] “Misr: Spatial resolution,” NASA, https://misr.jpl.nasa.gov/mission/misr-instrument/spatial-
resolution/ (accessed May 19, 2023).

[5] “tlcl_rh_bolton,” Tlcl_rh_bolton,
https://www.ncl.ucar.edu/Document/Functions/Contributed/tlcl_rh_bolton.shtml (accessed May
21, 2023) (Extras)

[6] Muñoz, Erith & Mundaray, Rafael & Falcon, Nelson. (2015). A Simplified Analytical Method
to Calculate the Lifting Condensation Level from a Skew-T Log-P Chart. Avances en Ciencias e
Ingenieria. 7. C124-C129 (Extras)

[7] Wmo, “Cumulonimbus,” International Cloud Atlas, https://cloudatlas.wmo.int/en/observation-
of-clouds-from-aircraft-descriptions-cumulonimbus.html (accessed May 21, 2023)
    