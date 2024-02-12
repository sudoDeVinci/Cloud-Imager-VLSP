import os
import cv2
import numpy as np
import numpy.typing
from gc import collect
from datetime import datetime
from enum import Enum


# For typing, these are inexact because out memory layout differences between Mat and UMat
Mat = numpy.typing.NDArray[np.uint8]
NDArray = numpy.typing.NDArray[any]


# Camera model for current visualization
class camera_models(Enum):
    OV2640 = "ov2640"
    OV5640 = "ov5640"
    DSLR = "dslr"

camera:str = camera_models['DSLR'].value


# Ensure path exists then return it.
def mkdir(folder:str) -> str:
    if not os.path.exists(folder): os.makedirs(folder)
    return folder


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
camera_distance_coefficients = mkdir(f"{calibration_folder}/distances")
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