from abc import ABC
from flask_login import UserMixin
from Devinci.config import *

class Role(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VISITOR = "visitor"
    UNKNOWN = "unknown"

    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, role:str):
        """
        Match input string to user role.
        """
        role = role.lower()
        return Role[role] if role in cls.__members__.items() else cls.UNKNOWN


    @classmethod
    @functools.lru_cache(maxsize=None)
    def __contains__(cls, role:str) -> bool:
        """
        Check if a role is present in the enum.
        """
        return role.lower() in cls.__members__.values()

class Entity(ABC):
    """
    Abstract Parent class representing a given row in a db table, either devices, sensors or readings. 
    """
    __slots__ = ("_MAC", "_timestamp")
    _MAC:str
    _timestamp:str

    def __init__(self, mac:str, stamp:str):
        self._MAC = mac
        self._timestamp = stamp
    
    def get_mac(self) -> str:
        return self._MAC
    
    def get_timestamp(self) -> str:
        return self._timestamp

class DeviceEntity(Entity):
    """
    Row of data in the Devices table.
    """
    _slots__ = ("_name", "_dev_model", "_cam_model", "_altitude", "_latitude", "_longitude")
    _name:str
    _dev_model:str
    _cam_model:camera_model
    _altitude:float
    _latitude:float
    _longitude:float

    @dispatch(str, str, str, str, float, float, float, timestamp = str)
    def __init__(self, mac:str, name:str, devmodel:str, cammodel:str,
                 alt:float, lat:float, long:float, timestamp: str = None):
        Entity.__init__(self, mac, timestamp)
        self._name = name
        self._dev_model = devmodel
        self._altitude = alt
        self._latitude = lat
        self._longitude = long
        self._cam_model = camera_model.match(cammodel)

    def get_name(self) -> str:
        return self._name
    
    def get_longitude(self) -> float:
        return self._longitude
    
    def get_latitude(self) -> float:
        return self._latitude
    
    def get_altitude(self) -> float:
        return self._altitude
    
    def get_dev_model(self) -> str:
        return self._dev_model
    
    def get_cam_model(self) -> str:
        return self._cam_model
    
    def set_name(self, n:str) -> None:
        self._name = n

class ReadingEntity(Entity):
    """
    Row of data in the Reading table.
    """
    __slots__ = ("_dewpoint", "_humidity", "_pressure", "_temperature", "_image_path")
    _temperature:float
    _humidity:float
    _pressure:float
    _dewpoint:float
    _image_path:str

    def __init__(self, mac:str, temp:float, humidity:float, pressure:float,
                dewpoint:float, timestamp:str, path:str = None):
        Entity.__init__(self, mac, timestamp)
        self._dewpoint = dewpoint
        self._humidity = humidity
        self._image_path = path
        self._pressure = pressure
        self._temperature = temp
    
    def get_dewpoint(self) -> float:
        return self._dewpoint
    
    def get_humidity(self) -> float:
        return self._humidity
    
    def get_pressure(self) -> float:
        return self._pressure
    
    def get_temperature(self) -> float:
        return self._temperature
    
    def get_image_path(self) -> str:
        return self._image_path
    
    def set_image_path(self, path:str) -> None:
        self._image_path = path

class SensorEntity(Entity):
    """
    Row of data in the senors table.
    """
    __slots__ = ("_sht", "_bmp", "_cam", "_wifi")
    _sht:bool
    _bmp:bool
    _cam:bool
    _wifi:bool

    def __init__(self, mac:str, timestamp:str, sht_stat:bool, bmp_stat:bool, cam_stat:bool, wifi_stat:bool = None):
        Entity.__init__(self, mac, timestamp)
        self._bmp = bmp_stat
        self._cam = cam_stat
        self._sht = sht_stat
        self._wifi = wifi_stat
    
    def get_sht(self) -> bool:
        return self._sht
    
    def get_bmp(self) -> bool:
        return self._bmp
    
    def get_cam(self) -> bool:
        return self._cam
    
    def get_wifi(self) -> bool:
        return self._wifi
    
    def set_sht(self, x:bool) -> None:
        self._sht = x
    
    def set_bmp(self, x:bool) -> None:
        self._bmp = x

    def set_cam(self, x:bool) -> None:
        self._cam = x

    def set_wifi(self, x:bool) -> None:
        self._wifi = x
    
    def allUp(self) -> bool:
        return (self.__sht and self.__bmp and self.__cam)

class LocationEntity(Entity):
    """
    Row of data in the locations table.
    """
    __slots__ = ("_country", "_region", "_city", "_latitude", "_longitude")
    _country:str
    _region:str
    _city:str
    _latitude:float
    _longitude:float

    def __init__(self, country:str, region:str, city:str, lat:float, lon:float):
        self._country = country
        self._region = region
        self._city = city
        self._latitude = lat
        self._longitude = lon

    def get_country(self) -> str:
        return self._country

    def get_region(self) -> str:
        return self._region

    def get_city(self) -> str:
        return self._city

    def get_latitude(self) -> float:
        return self._latitude

    def get_longitude(self) -> float:
        return self._longitude

class UserEntity(Entity, UserMixin):
    """
    Flask-compatible User Class Representation of User data row.
    """
    __slots__ = ("_ID", "_name", "_email", "_password", "_role", "_camera")
    _ID: str
    _name:str
    _email: str
    _password: str
    _role: Role
    _camera: Camera

    def __init__(self, id: str, name:str, email:str,
                password:str, role:Role, camera: Camera = None) -> None:
        self._ID = id
        self._name = name
        self._email = email
        self._password = password
        self._role = role 
        self._camera = camera

    def get_password(self) -> str:
        return self._password

    def get_name(self) -> str:
        return self._name
    
    def get_id(self):
        return self._ID
    
    def get_email(self) -> str:
        return self._email
    
    def get_role(self) -> Role:
        return self._role
    
    def get_camera(self) -> Camera:
        return self._camera