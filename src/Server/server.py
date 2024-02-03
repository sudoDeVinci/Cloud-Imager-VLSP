from flask import Flask, request, jsonify, Response, send_from_directory, send_file
import os
from analysis.config import debug
from db.Management import Manager
from db.Services import *
from Handlers import *

app = Flask(__name__)

# Define the directory to save images
# Ensure the upload directory exists
IMAGE_UPLOAD_DIR = "uploads"
os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)


@app.route("/update")
def update() -> Response:
    """
    Handler for the /update route on the server.
    Expect a GET request with the following:
    *  X-esp32-free-space=1310720,
    *  X-esp32-ap-mac=36:85:18:41:EB:78,
    *  Connection=close,
    *  X-esp32-version=0.0.1,
    *  X-esp32-sketch-size=1006448,
    *  Host=192.168.0.105:8084,
    *  User-agent=ESP32-http-Update,
    *  X-esp32-sketch-sha256=8DFFB149E1859BD81A0DF868C868F7127257065ED234C8D58247C347D416D758,
    *  X-esp32-chip-size=8388608,
    *  X-esp32-sta-mac=34:85:18:41:EB:78,
    *  X-esp32-sdk-version=v4.4.5,
    *  X-esp32-sketch-md5=d16dcda8e86f2bb80a68480a84db6460,
    *  X-esp32-mode=sketch,
    *  Cache-control=no-cache
    """
    try:
        # Get the timestamp from the "timestamp" header
        mac = request.headers.get('X-esp32-sta-mac')
        board_ver = request.headers.get('X-esp32-version')
        board_sha256 = request.headers.get("X-esp32-sketch-sha256")

        # Filter unwated Mac addresses
        #if mac_filter(mac):  return jsonify({"message": "No Current updates"}), 304

        conf_dict = load_config()
        FIRMWARE_FILE = conf_dict['path']
        
        firmware_version = conf_dict['version']
        
        #debug(f"Got data from {mac} \nBoard Firmware Version: {board_ver}\n Updated Firmware Version: {firmware_version}")

         
        if need_update(board_ver) :
            send_file(FIRMWARE_FILE, as_attachment=True)
        else:
            return jsonify({"message": "No Current updates"}), 304
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reading", methods = ['POST'])
def reading() -> Response:
    """
    Handler for the /reading route on the server.
    """
    try:
        # Get the timestamp from the "timestamp" header
        timestamp = request.headers.get('timestamp')
        mac = request.headers.get('MAC-Address')
        if not timestamp: return jsonify({"error": "Timestamp header is missing"}), 400
        debug(f"Got data from {mac} @ {timestamp}")

        temp = request.args.get('temperature')
        hum = request.args.get('humidity')
        pres = request.args.get('pressure')
        dew = request.args.get('dewpoint')

        debug(f"temp = {temp}\nhumidity = {hum}\npressure = {pres}\ndewpoint = {dew}")
        
        return jsonify({"message": "Thanks for the readings"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods = ['POST'])
def status() -> Response:
    """
    Handler for the /status on the server.
    Expecting a POST request in the form:
    * 
    * HEADER:
    * -------------------------------------
    * POST /<READINGPORT>  HTTP/1.1
    * Host: <IP>
    * Content-Type: application/x-www-form-urlencoded
    * Connection: close
    * Connection-Length: <LENGTH>
    * MAC-address: <MAC>
    * Timestamp: <Timestamp>
    * 
    * BODY:
    * 
    * sht=<bool>&bmp=<bool>&cam=<bool>
    """
    try:
        timestamp = request.headers.get('timestamp')
        if not timestamp: return jsonify({"error": "Timestamp header is missing"}), 400
        mac = request.headers.get('MAC-Address')
        debug(f"Got data from {mac} @ {timestamp}")

        # Should have a MAC filter.
        
        #debug(request.get_json())
        #debug(request.get_data())

        sht = request.args.get('sht')
        bmp = request.args.get('bmp')
        cam = request.args.get('cam')

        debug(f"SHT = {sht}\nBMP = {bmp}\nCAM = {cam}")
        
        return jsonify({"message": "Thanks for the stats"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/images', methods=['POST'])
def images() -> Response:
    """
    Handler for the /images in the server.
    """
    try:
        timestamp = request.headers.get('timestamp')
        mac = request.headers.get('MAC-Address')
        debug(f"Got data from {mac} @ {timestamp}")
        
        if not timestamp: return jsonify({"error": "Timestamp header is missing"}), 400
        
        image_raw_bytes = request.get_data()  #get the whole body

        # Assume the timestamp is already formatted
        # Create a filename based on the timestamp
        filename = f"{timestamp_to_path(timestamp)}.jpg"

        # Save the image to the specified directory
        image_path = os.path.join(IMAGE_UPLOAD_DIR, filename)
        with open(image_path, 'wb') as f:
            f.write(image_raw_bytes)

        return jsonify({"message": "Image saved successfully", "filename": filename}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
    finally:
        return jsonify({"message": "Nothing else"}), 500



if __name__ == '__main__':
    try:
        Manager.connect(True)
        if (not DeviceService.exists("34:85:18:40:CD:8C")): DeviceService.add("34:85:18:40:CD:8C", "Home-ESP", "ESP32S3", "OV5640", 173, 56.853470, 14.824620)
        if (not DeviceService.exists("34:85:18:41:EB:78")): DeviceService.add("34:85:18:41:EB:78", "Work-ESP", "ESP32S3", "OV5640", 173, 56.853470, 14.824620)
    except Exception as e:
        debug(e)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
    #app.run(host='0.0.0.0', port=8080, debug=True, ssl_context=('win_laptop.cer', 'win_laptop.pem'))