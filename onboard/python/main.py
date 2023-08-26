from network import WLAN, STA_IF
from time import sleep
from socket import socket

"""
Initialize camera settings
"""
def camera_init():
    import camera
    # Disable camera initialization
    camera.deinit()
    # Enable camera initialization
    camera.init(0, d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                format=camera.JPEG, framesize=camera.FRAME_VGA,
                xclk_freq=camera.XCLK_20MHz,
                href=23, vsync=25, reset=-1, pwdn=-1,
                sioc=27, siod=26, xclk=21, pclk=22, fb_location=camera.PSRAM)

    camera.framesize(camera.FRAME_VGA) # Set the camera resolution
    # The options are the following:
    # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
    # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
    # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA
    # Note: The higher the resolution, the more memory is used.
    # Note: And too much memory may cause the program to fail.

    camera.flip(1)                       # Flip up and down window: 0-1
    camera.mirror(0)                     # Flip window left and right: 0-1
    camera.saturation(0)                 # saturation: -2,2 (default 0). -2 grayscale
    camera.brightness(0)                 # brightness: -2,2 (default 0). 2 brightness
    camera.contrast(0)                   # contrast: -2,2 (default 0). 2 highcontrast
    camera.quality(10)                   # quality: # 10-63 lower number means higher quality
    # Note: The smaller the number, the sharper the image. The larger the number, the more blurry the image

    camera.speffect(camera.EFFECT_NONE)  # special effects:
    # EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO
    camera.whitebalance(camera.WB_NONE)  # white balance
    # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME


"""
Connect to wifi networks, either open or secured.
"""
def connect(SSID:str, PASSWORD:str, wlan:WLAN):
    import utime
    
    if PASSWORD is None:
        wlan.connect(ssid=SSID)
    else:
        wlan.connect(SSID, PASSWORD)
    print('connecting..',end='')
    start = utime.time()
    while not wlan.isconnected():
        utime.sleep(1)
        print('.',end='')
        if utime.time()-start > 5:
            break
    if wlan.isconnected():
        print('Connected on:', wlan.ifconfig()[0])
    return wlan.ifconfig()[3]


"""
Encode sht and bmp readings as bytes.
"""
def get_encoded_readings() -> bytes:
    from sensors import get_bmp_sht_readings
    sht_temp, sht_hum, bmp390_temp, bmp390_pressure, dewpoint = get_bmp_sht_readings()
    readings = "{0}|{1}|{2}|{3}|{4}".format(sht_temp, sht_hum, bmp390_temp, bmp390_pressure, dewpoint)
    return bytes(readings.encode('utf-8'))


"""
Given a socket/connection to send data over, pack the image then send it in a struct.
"""
def send_image(sock: socket):
    from camera import deinit, capture
    from struct import pack
    camera_init()
    
    try:
        # I capture multiple frames to skip them 
        capture()
        capture()
        buf = capture()

        length = len(buf)
        data = bytes(buf)
        print("Sending Image data..")
        
        # Send length (4-bytes).
        sock.sendall(pack('<I',length))
        # Send actual data packed in struct.
        sock.sendall(data)
        print("Image sent.")
        deinit()
        del buf, length, data
        collect()
        sleep(1)
    except Exception as e:
        print(e)
        socket.close()


"""
Given a socket/connection to send data over, pack the image then send it in a struct.
"""
def send_readings(sock: socket):
    from struct import pack

    readings = get_encoded_readings()
    length = len(readings)
    print("Sending Sensor data...")
    try:
        # Send length (4-bytes).
        sock.sendall(pack('<I',length))
        # Send actual data packed in struct.
        sock.sendall(readings)
        del readings, length
        sleep(1)
    except Exception as e:
        print(e)
        sock.close()
    


"""
Connect to a network using the credentials and send:
    1. 4-byte Packed Image Struct
    2. 4-byte Packed Weather Sensor Data Struct 
"""
def send_data():
    from socket import socket
    from gc import collect

    # Network credentials
    SSID = "Asimov-2.4GHZ"         
    PASSWORD = "Asimov42"
    wlan = WLAN(STA_IF)
    wlan.active(True)
    connect(SSID,PASSWORD,wlan)
    sleep(2)
    if not wlan.isconnected():
        return

    # Address hard-coded for testing.
    # In my original setting, the server would have simply
    # Sent it's details, with the fipy receiving via LTE.
    addr = "192.168.0.101"
    port = 88
    sock = socket()

    try:
        sock.connect((addr, port))
        # Send all data
        send_image(sock)
        send_readings(sock)
        
        # Close socket and disconnect wlan to save power.
        sock.close()
        wlan.disconnect()

        # Delete extra
        del wlan, sock

        collect()

    except Exception as e:
        print(e)
        if wlan:
            wlan.disconnect()
            del wlan
        if sock:
            sock.close()
        


if __name__  == "__main__":
    send_data()