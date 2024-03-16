import os
import cv2
import numpy as np
import numpy.typing
from gc import collect
from datetime import datetime
from enum import Enum
from typing import List, Sequence, Tuple
import tomllib as toml



class camera_model(Enum):
    """
    Enum holding the various camera modules information.
    To be expanded later.
    """
    OV2640 = "ov2640"
    OV5640 = "ov5640"
    DSLR = "dslr"

# Camera model for current visualization
camera:str = camera_model['OV5640'].value


# For typing, these are inexact because out memory layout differences such as between Mat and UMat
Mat = numpy.typing.NDArray[np.uint8]
Matlike = cv2.typing.MatLike
NDArray = numpy.typing.NDArray[any]



# Ensure path exists then return it.
def mkdir(folder:str) -> str:
    """
    Ensure a directory exists and return path to it.
    """
    if not os.path.exists(folder): os.makedirs(folder)
    return folder


# Database related folders
db_schema_folder = mkdir('schemas')


# Various Image folders
root_image_folder = 'images'
blocked_images_folder = mkdir(f"{root_image_folder}/blocked_{camera}")
reference_images_folder = mkdir(f"{root_image_folder}/reference_{camera}")
cloud_images_folder = mkdir(f"{root_image_folder}/cloud_{camera}")
sky_images_folder = mkdir(f"{root_image_folder}/sky_{camera}")
root_graph_folder = mkdir('Graphs')


# Calibration image paths and settings  
calibration_folder = "calibration"
calibration_images = mkdir(f"{calibration_folder}/images")
camera_matrices = mkdir(f"{calibration_folder}/matrices")
undistorted_calibration_images = mkdir(f"{calibration_folder}/undistorted")
distorted_calibration_images = mkdir(f"{calibration_folder}/distorted")
calibration_config = "calibration_cfg.toml"


# If debug is True, print. Otherwise, do nothing.
DEBUG:bool = True
def out01(x:str) -> None:
    print(x)
def out02(x:str) -> None:
    pass
debug = out01 if DEBUG else out02


# Functions for reading and writing from toml files.
# Most/all of the config files use toml format for simplicity.
def write_toml(data:dict, path:str) -> None:
    """
    Write to a toml file.
    """
    try:
        with open(path, "w") as f:
            toml.dump(data, f)
    except Exception as e:
        debug(f"Error writing to TOML file: {e}")


def load_toml(file_path:str) -> dict:
    """ 
    Attempt to load a toml file as a dictionary.
    """
    toml_data = None
    try:
        with open(file_path, 'rb') as file:
            toml_data = toml.load(file)
            if not toml_data: return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except toml.TOMLDecodeError as e:
        print(f"Error decoding TOML file: {e}")
        return None

    return toml_data


def __load_pkl_resource(folder:str, name:str) -> Mat:
    """
    Attempt to load pickled resource <name> from <folder>.
    """
    import pickle
    try:
        with open(f"{folder}/{name}", "rb" ) as file:
            out = pickle.load(file)
    except FileNotFoundError:
        debug(f"Error: File '{folder}/{name}' not found.")
        return None

    return out