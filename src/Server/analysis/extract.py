from PIL import Image
from src.Server.analysis.config import *
from typing import Callable
from scipy import stats

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
        case 3:
            components = ['','','']
            colour_tag = 'cymk'
        case _:
            components = None
            colour_tag = None

    out = [components, colour_tag]
        
    return out

def __process_RGB(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in RGB format.
    """
    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < red) & (0 < green) & (0 < blue))
    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
    return non_black_data

def __process_HSV(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in HSV format.
    """
    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < v) & (0 < s) & (0 < h))
    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))
    return non_black_data

def __process_YBR(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in YcBcR format.
    """
    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < Y))
    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
    return non_black_data

def __count(xyz_sk: NDArray) -> NDArray:
    """
    Return a frequency table of the integers in an input array
    """
    unique, counts = np.unique(xyz_sk, return_counts=True)
    freq = np.asarray((unique, counts)).T
    return freq

def raw_images(folder_path:str, colour_index: int = 0) -> NDArray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    """
    data = []
    for filename in os.listdir(folder_path):
        if (not filename.endswith(".png") 
            and not filename.endswith(".jpg") 
            and not filename.endswith(".jpeg")):
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

def get_func(colour_index: int) -> Callable[[NDArray], NDArray]:
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
            
def remove_outliers_iqr(data: NDArray) -> NDArray:
    """
    Remove outliers from data using IQR.
    Data points that fall below Q1 - 1.5 IQR or above the third quartile Q3 + 1.5 IQR are outliers.
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data >= lower_bound) & (data <= upper_bound)]

def remove_outliers_z_score(data: NDArray, threshold: float = 3.0) -> NDArray:
    """
    Remove outliers from data using the Z-score method.
    Data points with a Z-score greater than the threshold will be considered as outliers.
    """
    z_scores = np.abs(stats.zscore(data))
    return data[(z_scores < threshold).all(axis=1)]

def __check_distribution(data: NDArray, label:str):
    distributions = {
        "Normal": {"func": stats.norm, "params": stats.norm.fit(data)},
        "Beta": {"func": stats.beta, "params": stats.beta.fit(data)},
        "Chi-Squared": {"func": stats.chi2, "params": stats.chi2.fit(data)}
    }

    results = {}
    for dist_name, dist in distributions.items():
        _, p_value = stats.kstest(data, dist["func"].name, args=dist["params"])
        results[dist_name] = p_value

    # Print the results
    print(f"Distribution Test Results - {label}")
    for dist_name, p_value in results.items():
        print(f"{dist_name}: p-value = {p_value:.4f}")

    return results