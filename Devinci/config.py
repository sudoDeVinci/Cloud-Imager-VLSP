import os
import cv2
import numpy as np
import numpy.typing
from gc import collect
import functools
from datetime import datetime
from enum import Enum
from typing import List, Sequence, Tuple, Dict, NamedTuple, Any, Iterable, TypeVar, TypeAlias, Optional, Self
import toml
from multipledispatch import dispatch 
import json
from abc import ABC



COLOUR_MARKERS:List[tuple[str,str]] = [
    ('b', 'o'),  # blue, circle
    ('g', '^'),  # green, triangle up
    ('r', 's'),  # red, square
    ('c', 'D'),  # cyan, diamond
    ('m', 'p'),  # magenta, pentagon
    ('y', '*'),  # yellow, star
    ('k', 'x'),  # black, x
    ('#FFA07A', 'H'),  # LightSalmon, hexagon1
    ('#20B2AA', 'v'),  # LightSeaGreen, triangle down
    ('#8A2BE2', '8'),  # BlueViolet, octagon
    ('#7FFF00', 'D'),  # Chartreuse, diamond
    ('#FF4500', 'h'),  # OrangeRed, hexagon2
    ('#9932CC', 'p'),  # DarkOrchid, pentagon
    ('#3CB371', 'X'),  # MediumSeaGreen, x
    ('#40E0D0', 'd'),  # Turquoise, thin_diamond
    ('#FFD700', '+'),  # Gold, plus
    ('#DC143C', '|'),  # Crimson, vline
    ('#800080', '_')   # Purple, hline
]

# Ensure path exists then return it.
def mkdir(folder:str) -> str:
    """
    Ensure a directory exists and return path to it.
    """
    if not os.path.exists(folder): os.makedirs(folder)
    return folder

ROOT = os.path.join(os.getcwd(), "Devinci", "static")
IMAGE_UPLOADS = mkdir(os.path.join(ROOT,"uploads"))

# Various config files
root_config_folder = mkdir('configs')
FIRMWARE_CONF:str = os.path.join(root_config_folder, "firmware_cfg.toml")
DB_CONFIG:str = os.path.join(root_config_folder, "db_cfg.toml")

IMAGE_TYPES = ("jpg","png","jpeg","bmp","svg")


class camera_model(Enum):
    """
    Enum holding the various camera modules information.
    To be expanded later.
    """
    OV2640 = "ov2640"
    OV5640 = "ov5640"
    DSLR = "dslr"
    IPHONE13MINI = "iphone13mini"
    UNKNOWN = "unknown"

    @classmethod
    
    def match(cls, camera:str):
        """
        Match input string to camera model.
        """
        camera = camera.lower()
        for _, camtype in cls.__members__.items():
            if camera == camtype.value: return camtype
        return cls.UNKNOWN

    @classmethod
    @functools.lru_cache(maxsize=None)
    def __contains__(cls, camera:str) -> bool:
        """
        Check if a camera model is supported.
        """
        return camera_model.match(camera) != cls.UNKNOWN

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN
    
    @classmethod
    def members(cls) -> List[Self]:
        return [ctype for _, ctype in cls.__members__.items()]
    
    @classmethod
    def names(cls) -> List[str]:
        return [names for names, _ in cls.__members__.items()]

class Optical(ABC):
    isClass = None

class Camera(Optical):
    """
    Camera class wrapper to automatically handle the format
    of various paths for a specific camera.
    """

    def __init__(self, Model: camera_model):
        self._Model = Model
        root_folder = ROOT

        # Graphing paths
        self.root_graph_folder = os.path.join(root_folder, 'Graphs', Model.value)
        self.histogram_folder = mkdir(os.path.join(self.root_graph_folder, 'hist'))
        self.pca_folder = mkdir(os.path.join(self.root_graph_folder, 'pca'))
        self.roc_folder = mkdir(os.path.join(self.root_graph_folder, 'roc'))
        self.cache_folder = mkdir(os.path.join(self.root_graph_folder, 'cache'))

        # Various Image folders
        self.root_image_folder = os.path.join(root_folder, "images", Model.value)
        self.blocked_images_folder = self.mkdir(os.path.join(self.root_image_folder, 'blocked'))
        self.reference_images_folder = self.mkdir(os.path.join(self.root_image_folder, 'reference'))
        self.cloud_images_folder = self.mkdir(os.path.join(self.root_image_folder, 'cloud'))
        self.sky_images_folder = self.mkdir(os.path.join(self.root_image_folder, 'sky'))
        self.sky_masks_folder = self.mkdir(os.path.join(self.root_image_folder, 'masks', 'sky'))
        self.cloud_masks_folder = self.mkdir(os.path.join(self.root_image_folder, 'masks', 'cloud'))

        # Calibration image paths and settings
        self.calibration_folder = os.path.join(root_folder, "calibration", Model.value)
        self.camera_matrices = self.mkdir(os.path.join(self.calibration_folder, 'matrices'))
        self.training_calibration_images = self.mkdir(os.path.join(self.calibration_folder, 'trainers'))
        self.undistorted_calibration_images = self.mkdir(os.path.join(self.calibration_folder, 'undistorted'))
        self.distorted_calibration_images = self.mkdir(os.path.join(self.calibration_folder, 'distorted'))
        self.CALIBRATION_CONFIG = os.path.join(self.calibration_folder, 'calibration_cfg.toml')

        # Various config files
        root_config_folder = 'configs'


    @dispatch(Optical)
    def __eq__(self, value: Optical) -> bool:
        return super().__eq__(value)

    @dispatch(camera_model)
    def __eq__(self, other: camera_model) -> bool:
        return other == self._Model.value

    @dispatch(str)
    def __eq__(self, name: str) -> bool:
        return name.lower() == self._Model.value.lower()

    def mkdir(self, path: str):
        """
        Create directories if they do not exist.
        """
        os.makedirs(path, exist_ok=True)
        return path
    
    @property
    def Model(self) -> camera_model:
        """
        Return the camera model.
        """
        return self._Model

# For typing, these are inexact because out memory layout differences such as between Mat and UMat
Mat = cv2.Mat
Matlike = cv2.typing.MatLike
NDArray = numpy.typing.NDArray[any]
intp = np.intp



# If debug is True, print. Otherwise, do nothing.
DEBUG:bool = True
def out01(x:str) -> None:
    print(x)
def out02(x:str) -> None:
    pass
debug = out01 if DEBUG else out02


# Functions for reading and writing from toml files.
# Most\\all of the config files use toml format for simplicity.
def write_toml(data:Dict, path:str) -> None:
    """
    Write to a toml file.
    """
    try:
        out = toml.dumps(data)
        with open(path, "w") as f:
            f.write(out)
    except Exception as e:
        debug(f"Error writing to TOML file: {e}")


def load_toml(file_path:str) -> Dict[str , Any] | None:
    """ 
    Attempt to load a toml file as a dictionary.
    """
    toml_data = None
    try:
        with open(file_path, 'r') as file:
            toml_data = toml.load(file)
            if not toml_data: return None
    except FileNotFoundError:
        debug(f"Error: File '{file_path}' not found.")
        return None
    except toml.TomlDecodeError as e:
        debug(f"Error decoding TOML file: {e}")
        return None

    return toml_data

def load_json(file_path: str) ->Dict[str , Any] | None:
    """
    Attempt to load JSON file data as a dictionary.
    """
    data = None
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if not data: return None
    except FileNotFoundError:
        debug(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        debug(f"Error decoding JSON file: {e}")
        return None
    
def write_json(data: Dict[str, Any], path: str) -> None:
    """
    Write dictionary data to a JSON file.
    """
    try:
        out = json.dumps(data)
        with open(path, "w") as f:
            f.write(out)
    except Exception as e:
        debug(f"Error writing to JSON file: {e}")

import pickle

def unpickle_file(path: str) -> List | Dict: 
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        out = pickle.load(f) # deserialize using load()
    
    return out

def pickle_file(path: str, data: str) -> None:
    with open(path, 'wb') as f:
        pickle.dump(data, f) # serialize using dump()