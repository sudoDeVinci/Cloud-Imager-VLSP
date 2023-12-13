from PIL import Image
from config import *

def __process_RGB(image: np.array) -> np.array:
    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((red != 0) | (green != 0) | (blue != 0))
    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
    return non_black_data

def __process_HSV(image: np.array) -> np.array:
    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((v != 0))
    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))
    return non_black_data

def __process_YBR(image: np.array) -> np.array:
    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((Y != 0))
    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
    return non_black_data

def process_images(folder_path:str, colour_index: int = 0) -> np.ndarray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    """
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image = Image.open(os.path.join(folder_path, filename))

            match colour_index:
                case 0:
                    image = np.array(image)
                    non_black_data = __process_RGB(image)
                    
                    
                case 1:
                    image = image.convert('HSV')
                    image = np.array(image)
                    non_black_data = __process_HSV(image)

                case 2:
                    image = image.convert('YCbCr')
                    image = np.array(image)
                    non_black_data = __process_YBR(image)
                
                case _:
                    image = np.array(image)
                    non_black_data = __process_RGB(image)
            
            # Mean-centering
            non_black_data = non_black_data - np.mean(non_black_data, axis=0)
            
            data.append(non_black_data)
    return np.vstack(data)

def raw_images(folder_path:str, colour_index: int = 0) -> np.ndarray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    """
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image = Image.open(os.path.join(folder_path, filename))

            match colour_index:
                case 0:
                    image = np.array(image)
                    non_black_data = __process_RGB(image)
                    
                    
                case 1:
                    image = image.convert('HSV')
                    image = np.array(image)
                    non_black_data = __process_HSV(image)

                case 2:
                    image = image.convert('YCbCr')
                    image = np.array(image)
                    non_black_data = __process_YBR(image)
                
                case _:
                    image = np.array(image)
                    non_black_data = __process_RGB(image)
            
            data.append(non_black_data)
    return np.vstack(data)