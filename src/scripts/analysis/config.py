import os
import cv2
import numpy as np
import numpy.typing
from gc import collect
from datetime import datetime

# For typing
Mat = numpy.typing.NDArray[np.uint8]

# Camera model for current visualization
camera = "dslr"

# Global paths

def mkdir(folder:str) -> str:
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


root_image_folder = 'images'
blocked_images_folder = mkdir(f"{root_image_folder}/blocked_{camera}")
reference_images_folder = mkdir(f"{root_image_folder}/reference_{camera}")
cloud_images_folder = mkdir(f"{root_image_folder}/cloud_{camera}")
sky_images_folder = mkdir(f"{root_image_folder}/sky_{camera}")
root_graph_folder = mkdir('Graphs')


# If debug is True, our debug lines throughtout the code will print. Otherwise, do nothing
DEBUG:bool = True
def out01(x:str) -> None:
    print(x)
def out02(x:str) -> None:
    pass
debug = out01 if DEBUG else out02

