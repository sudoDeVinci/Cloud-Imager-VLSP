from os import name
from Devinci.config import debug
from Devinci.db.Entities import Role
from Devinci.db.Management import Manager
from Devinci.db.services.device import DeviceService
from Devinci.db.services.user import UserService
from Devinci.db.backup import backup
from Devinci import create_app

from Devinci.config import debug, DB_CONFIG

from werkzeug.security import generate_password_hash, check_password_hash

# from Devinci.db.services.user import UserService
# from werkzeug.security import generate_password_hash

app = create_app()

if __name__ == "__main__":
    # from waitress import serve

    try:
        Manager.connect(False)
        backup()
        print(DB_CONFIG)
        if not DeviceService.exists("34:85:18:40:CD:8C"): DeviceService.add("34:85:18:40:CD:8C", "Home-ESP", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if not DeviceService.exists("34:85:18:41:EB:78"): DeviceService.add("34:85:18:41:EB:78", "Work-ESP", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if not DeviceService.exists("34:85:18:41:59:14"): DeviceService.add("34:85:18:41:59:14", "ESP001", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if not DeviceService.exists("34:85:18:42:6D:94"): DeviceService.add("34:85:18:42:6D:94", "ESP002", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
    except Exception as e:
        debug(e)
    
    app.config['SECRET_KEY'] = Manager.get_sk()
    app.run(host="0.0.0.0", port = 8080)