import numpy as np
import numpy.typing
from datetime import datetime
import cv2
import os

# For typing
Mat = numpy.typing.NDArray[np.uint8]

# Camera model
camera = "dslr"

# Global paths
root_image_folder = 'images'
blocked_images_folder = f"{root_image_folder}/blocked_{camera}"
reference_images_folder = f"{root_image_folder}/reference_{camera}"
cloud_images_folder = f"{root_image_folder}/cloud_{camera}"
sky_images_folder = f"{root_image_folder}/sky_{camera}"

root_graph_folder = 'Graphs'


DEBUG:bool = True
def out01(x:str) -> None:
    print(x)
def out02(x:str) -> None:
    pass
debug = out01 if DEBUG else out02

