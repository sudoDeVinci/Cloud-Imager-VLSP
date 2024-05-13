from Devinci.db.Entities import *
from Devinci.db.services.device import DeviceService
from Devinci.db.services.user import UserService
from Devinci.db.services.status import StatusService
from Devinci.db.services.reading import ReadingService
from Devinci.db.services.location import LocationService
from Devinci.db.schema import apply, sqlite

BACKUP_DIR = mkdir('backups')

def _add_devices(conn: sqlite.Connection,
        MAC: str,
        name: str,
        dev_model: str,
        cam_model: camera_model,
        altitude: float,
        latitude: float,
        longitude: float) -> None:
        
        cursor = None
        # Insert records into the database.
        insert_string = "INSERT INTO Devices VALUES(?, ?, ?, ?, ?, ?, ?);"

        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (MAC, name, dev_model, cam_model.value, altitude, latitude, longitude)
            )

            conn.commit()

        except sqlite.Error as e:
            debug(f"Couldn't insert device record -> {e}")

        finally:
            if cursor: cursor.close()


def backup() -> None:
    devices: List[DeviceEntity] = DeviceService.get_all()
    #users: List[UserEntity] = UserService.get_all()
    #statuses: List[SensorEntity] = StatusService.get_all()
    #readings: List[ReadingEntity] = ReadingService.get_all()
    #locations: List[LocationEntity] = LocationService.get_all()
    
    timestamp = datetime.now()
    BACKUP_PATH = os.path.join(BACKUP_DIR, f'{timestamp.strftime('%Y-%m-%d-%H-%M-%S')}.db')
    conn: sqlite.Connection = sqlite.connect(BACKUP_PATH)
    apply(conn)
    for device in devices:
        _add_devices(   conn,
                        device.get_mac(),
                        device.get_name(),
                        device.get_dev_model(),
                        device.get_cam_model(),
                        device.get_altitude(),
                        device.get_latitude(),
                        device.get_longitude()
                    )