import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from gc import collect
import os
import cv2
from datetime import datetime
from colour_graphs import filesync

# Camera model
camera = "dslr"

# Global paths
root_image_folder = 'CloudMeshVLSP/images'
blocked_images_folder = f"{root_image_folder}/blocked_{camera}"
reference_images_folder = f"{root_image_folder}/reference_{camera}"
cloud_images_folder = f"{root_image_folder}/cloud_{camera}"
sky_images_folder = f"{root_image_folder}/sky_{camera}"

root_graph_folder = 'CloudMeshVLSP/Graphs'

# TODO: Better histogram generation


def analyze() -> None:
    pass


def __process_images(folder_path:str, colour_index: int = 0) -> np.ndarray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    """
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image = Image.open(os.path.join(folder_path, filename))

            # Differences in colour channel format require diffrent ways of filtering for black pixels in binary images.
            match colour_index:
                case 0:
                    image = np.array(image)
                    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
                    non_black_indices = np.where((red != 0) | (green != 0) | (blue != 0))
                    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
                    
                case 1:
                    image = image.convert('HSV')
                    image = np.array(image)
                    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
                    non_black_indices = np.where((v != 0))
                    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))

                case 2:
                    image = image.convert('YCbCr')
                    image = np.array(image)
                    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
                    non_black_indices = np.where((Y != 0))
                    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
                
                case _:
                    image = np.array(image)
                    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
                    non_black_indices = np.where((red != 0) | (green != 0) | (blue != 0))
                    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
            
            data.append(non_black_data)
    return np.vstack(data)



def filesync(blc:str, ref:str, cld:str, sky:str) -> bool:
    """
    Make sure filenames are synced before running
    """
    for (_, _, b_imgs), (_, _, r_imgs),(_, _, c_imgs),(_, _, s_imgs) in zip (os.walk(blc),os.walk(ref),os.walk(cld),os.walk(sky)):
        for b_img, r_img, c_img, s_img in zip(b_imgs, r_imgs, c_imgs, s_imgs):
            if not (b_img == r_img == c_img == s_img):
                print(f"Image Desync!\nRef: {r_img}\nBlocked: {b_img}\nCloud: {c_img}\nSky: {s_img}")
                return False 
    print("Files Synced")
    return True



def __separate(blocked_image_path: str, reference_image_path: str, count:int) -> None:
    num = str(count).zfill(2)
    b_img = cv2.imread(blocked_image_path)
    r_img = cv2.imread(reference_image_path)
    
    b_img = cv2.resize(b_img,(400, 300))
    r_img = cv2.resize(r_img,(400, 300))

    b_img = cv2.cvtColor(b_img, cv2.COLOR_BGR2HSV)
    r_img = cv2.cvtColor(r_img, cv2.COLOR_BGR2HSV)

    
    """
    First we make a mask for red colours
    We'll use Red to represent Clouds
    Red can have hue values between 0-10, but also 170-180
    """

    u_b_red1HSV = np.array([10, 255, 255])
    l_b_red1HSV = np.array([0, 30, 30])

    u_b_red2HSV = np.array([180, 255, 255])
    l_b_red2HSV = np.array([170, 50, 50])

    maskOneRedHSV = cv2.inRange(b_img,l_b_red1HSV,u_b_red1HSV)
    maskTwoRedHSV = cv2.inRange(b_img,l_b_red2HSV,u_b_red2HSV)

    redMask = cv2.bitwise_or(maskOneRedHSV,maskTwoRedHSV)

    """
    Now we do the same for Black.
    We'll use a range of black to represent The Sky
    """

    u_b_blackHSV = np.array([180, 255,30])
    l_b_blackHSV = np.array([0, 0, 0])

    blackMask = cv2.inRange(b_img, l_b_blackHSV, u_b_blackHSV)


    """
    Apply masks and create HSV versions of our images.
    """

    cloud_img = cv2.bitwise_and(r_img, r_img, mask = redMask)
    sky_img = cv2.bitwise_and(r_img, r_img, mask = blackMask)
    c_img = cv2.cvtColor(cloud_img, cv2.COLOR_HSV2BGR)
    s_img = cv2.cvtColor(sky_img, cv2.COLOR_HSV2BGR)

    cv2.imwrite(f"{cloud_images_folder}/Image{num}.png",c_img)
    cv2.imwrite(f"{sky_images_folder}/Image{num}.png",s_img)



def separate_datasets(blocked_image_folder: str, reference_image_folder: str) -> None:
    """
    This iterates through colour-blocked images and separates them into two images, one sky and one cloud

    An assumption of this function is that all images are of the same size.
    As to not raise an error
    """
    count = 1
    for (ref_root, _, referenceImages), (blc_root, _, blockedImages) in zip(os.walk(reference_image_folder), os.walk(blocked_image_folder)):
        for ref, blc in zip(referenceImages, blockedImages):
            refPath = os.path.join(ref_root, ref)
            blockPath = os.path.join(blc_root, blc)
            __separate(blockPath, refPath, count)
            count+=1