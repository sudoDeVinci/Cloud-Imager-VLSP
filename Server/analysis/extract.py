from PIL import Image
from config import *

def get_tags(colour_index:int) -> list[list[str, str, str], str]:
    """
    Get the colour tags and accompanying label for a given index.
    """
    match colour_index:

        case 0:
            components = ['red', 'green', 'blue']
            colour_tag = 'RGB'
        case 1:
            components = ['hue','saturation','value']
            colour_tag = 'HSV'
        case 2:
            components = ['brightness','Chroma Blue','Chroma Red']
            colour_tag = 'YCbCr'
        case _:
            components = None
            colour_tag = None

    out = [components, colour_tag]
        
    return out

def __process_RGB(image: np.array) -> np.array:
    """
    Extract the non-black pixels from a colour-masked image in RGB format.
    """
    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((red != 0) | (green != 0) | (blue != 0))
    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
    return non_black_data

def __process_HSV(image: np.array) -> np.array:
    """
    Extract the non-black pixels from a colour-masked image in HSV format.
    """
    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((v != 0))
    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))
    return non_black_data

def __process_YBR(image: np.array) -> np.array:
    """
    Extract the non-black pixels from a colour-masked image in YcBcR format.
    """
    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((Y != 0))
    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
    return non_black_data

def process_images(folder_path:str, colour_index: int = 0) -> np.ndarray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    Return the image data centered around the mean of the non-black data.
    """
    data = []
    for filename in os.listdir(folder_path):
        if (not filename.endswith(".png")):
            continue
    
        im = Image.open(os.path.join(folder_path, filename))
        tag = get_tags(colour_index)[1]

        __process = get_func(colour_index)

        if tag != 'RGB':
            im = im.convert(tag)
        im = np.array(im)
        non_black_data = __process(im)

        
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
        if (not filename.endswith(".png")):
            continue
    
        im = Image.open(os.path.join(folder_path, filename))
        tag = get_tags(colour_index)[1]

        __process = get_func(colour_index)

        if tag != 'RGB':
            im = im.convert(tag)
        im = np.array(im)
        non_black_data = __process(im)
            
        data.append(non_black_data)
        
    return np.vstack(data)

def raw_largest_separations(folder_path:str):
    """_summary_

    Args:
        folder_path (str): _description_
    """
    data = []
    for filename in os.listdir(folder_path):
        if (not filename.endswith(".png")):
            continue
    
        im = Image.open(os.path.join(folder_path, filename))

        non_black_data = __process_RGB(im)

        im_hsv = im.convert('HSV')
        image = np.array(im)
        non_black_data = __process_HSV(im)

        image = im.convert('YCbCr')
        image = np.array(im)
        non_black_data = __process_YBR(im)


def get_func(colour_index: int):
    """_summary_

    Args:
        colour_index (int): _description_

    Returns:
        function: _description_
    """
    match colour_index:

            case 0:
                return __process_RGB

            case 1:
                return __process_HSV

            case 2:
                return __process_YBR
            
            case _:
                return __process_RGB
            
    