from __future__ import annotations
from Devinci.config import *

from PIL import Image
from typing import Callable


def process_RGB(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in RGB format.
    """
    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < red) & (0 < green) & (0 < blue))
    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
    return non_black_data

def process_HSV(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in HSV format.
    """
    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < v) & (0 < s) & (0 < h))
    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))
    return non_black_data

def process_YBR(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in YcBcR format.
    """
    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < Y))
    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
    return non_black_data


class Colour_Tag(Enum):
    """
    A Colour Tag holds a dictionary of relelvant values to an image of a specific
    colour space.

    ## Fields
    
    #### 'components': List[str, str, str]
        - A 3-tuple of the colour channels in order.
    
    #### 'tag': str
        - The corresponding tag used by Pillow when converting to the colour space.
    
    #### 'converter': int
        - The OpenCV COLOR_BGR2<target> constant for the color space.

    #### 'func': Callable[[NDArray], NDarray]
        - The function used to get non-black data from a set of images stacked as an NDArray.
    """

    RGB = {
        'components' : ('Red', 'Green', 'Blue'),
        'tag' : 'RGB',
        'converter' : cv2.COLOR_BGR2RGB,
        'func' : process_RGB
           }
    HSV = {
        'components': ('Hue','Saturation','Value'),
        'tag' : 'HSV',
        'converter': cv2.COLOR_BGR2HSV,
        'func' : process_HSV
            }
    YCRCB = {
        'components' : ('Brightness','Chroma Red','Chroma Blue'), 
        'tag' : 'YCbCr',
        'converter' : cv2.COLOR_BGR2YCrCb,
        'func' : process_YBR
            }
    UNKNOWN = {
        'components' : None,
        'tag' : "UNKNOWN",
        'converter' : None,
        'func' : None}

    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, tag_str:str) -> Self:
        """
        Match input string to camera model.
        """
        tag_str = tag_str.upper()
        for _, tagtype in cls.__members__.items():
            if tag_str == tagtype.value['tag'].upper(): return tagtype
        return cls.UNKNOWN
    
    @classmethod
    def members(cls) -> List[Self]:
        return [ttype for _, ttype in cls.__members__.items()]
    

class Boundary():
    isClass = None

class ChannelBound(Boundary):
    """
    The Boundaries of the distribution for a given colour channel.
    Used during colour-boundary analysis to represent a point on an ROC graph.
    """

    __slots__ = ('_lower_bound', '_upper_bound', '_channel', '_False_Positive_Rate', '_True_Positive_Rate', '_Precision')

    def __init__(self,
                 lower_bound: int,
                 upper_bound: int,
                 channel: str,
                 True_Pos: float = None,
                 False_Pos: float = None,
                 pres: float = None,
                 acc: float = None):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._channel = channel
        self._True_Positive_Rate = True_Pos
        self._False_Positive_Rate = False_Pos
        self._Precision = pres
        self._Accuracy = acc


    @property
    def False_Positive_Rate(self) -> float:
        return self._False_Positive_Rate

    @property
    def True_Positive_Rate(self) -> float:
        return self._True_Positive_Rate
    
    @property
    def Precision(self) -> float:
        return self._Precision
    
    @property
    def lower_bound(self) -> int:
        return self._lower_bound
    
    @property
    def upper_bound(self) -> int:
        return self._upper_bound
    
    @property
    def channel(self) -> str:
        return self._channel
    
    @property
    def Accuracy(self) -> float:
        return self._Accuracy

    def _ChannelBoundCheck(self, obj: Self) -> None:
        if not isinstance(obj, Boundary): 
            debug(f"unsupported operand for + on ChannelBound and {type(obj)}")
            raise TypeError()
        if self.channel != obj.channel: raise TypeError()
        if self.lower_bound != obj.lower_bound: raise TypeError()
        if self.upper_bound != obj.upper_bound: raise TypeError()

    
    def __add__(self, obj: Self) -> Self:
        self._ChannelBoundCheck(obj)

        return ChannelBound(lower_bound = self.lower_bound,
                            upper_bound = self.upper_bound,
                            channel = self.channel,
                            True_Pos = self._True_Positive_Rate + obj.True_Positive_Rate,
                            False_Pos= self._False_Positive_Rate + obj.False_Positive_Rate,
                            pres = self._Precision + obj.Precision,
                            acc = self.Accuracy + obj.Accuracy)
    
    def __sub__(self, obj: Self) -> Self:
        self._ChannelBoundCheck(obj)

        return ChannelBound(lower_bound = self.lower_bound,
                            upper_bound = self.upper_bound,
                            channel = self.channel,
                            True_Pos = self._True_Positive_Rate - obj.True_Positive_Rate,
                            False_Pos = self._False_Positive_Rate - obj.False_Positive_Rate,
                            pres = self._Precision - obj.Precision,
                            acc = self._Accuracy - obj.Accuracy)
    
    @dispatch(Boundary)
    def __mul__(self, obj: Self) -> Self:
        self._ChannelBoundCheck(obj)

        return ChannelBound(lower_bound = self.lower_bound,
                            upper_bound = self.upper_bound,
                            channel = self.channel,
                            True_Pos = self._True_Positive_Rate * obj.True_Positive_Rate,
                            False_Pos = self._False_Positive_Rate * obj.False_Positive_Rate,
                            pres = self._Precision * obj.Precision,
                            acc = self._Accuracy * obj.Accuracy)
    
    @dispatch(float)
    def __mul__(self, num: float) -> Self:

        return ChannelBound(lower_bound = self.lower_bound,
                            upper_bound = self.upper_bound,
                            channel = self.channel,
                            True_Pos = self._True_Positive_Rate * num,
                            False_Pos = self._False_Positive_Rate * num,
                            pres = self._Precision * num,
                            acc = self._Accuracy * num)
    
    @dispatch(int)
    def __mul__(self, num: int) -> Self:
        return self.__mul__(float(num))
        
    
    @dispatch(float)
    def __truediv__(self, num: float) -> Self:
        return ChannelBound(lower_bound = self.lower_bound,
                            upper_bound = self.upper_bound,
                            channel = self.channel,
                            True_Pos = self._True_Positive_Rate / num,
                            False_Pos = self._False_Positive_Rate / num,
                            pres = self._Precision / num,
                            acc = self._Accuracy / num)
    
    @dispatch(int)
    def __truediv__(self, num: int) -> Self:
        return self.__truediv__(float(num))

    


    def __repr__(self):
        return f"{self.channel} | ({self.lower_bound}:{self.upper_bound}) | ({self._False_Positive_Rate:.3f}, {self._True_Positive_Rate:.3f}) | ({self._Precision:.3f}, {self._True_Positive_Rate:.3f})"


def _is_image(name: str) -> bool:
    for filetype in IMAGE_TYPES:
        if name.endswith(f".{filetype}"): return True
    return False

def get_nonblack_all(folder_path:str, colour_tag: Colour_Tag) -> NDArray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    """
    data = []
    images = tuple(filename for filename in os.listdir(folder_path))

    for filename in images:
        if not _is_image(filename): continue
    
        im = Image.open(os.path.join(folder_path, filename))
        tag:str = colour_tag.value['tag']

        __process:Callable[[NDArray], NDArray] = colour_tag.value['func']

        if tag != 'RGB': 
            im = im.convert(tag)
        im = np.array(im, dtype = np.uint8)
        non_black_data = __process(im)
            
        data.append(non_black_data)
        
    return np.vstack(data)

def get_nonblack(image_paths: str, colour_tag: Colour_Tag) -> NDArray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    """
    data = []
    for filename in image_paths:
        if not _is_image(filename): continue
    
        im = Image.open(filename)
        tag:str = colour_tag.value['tag']

        __process:Callable[[NDArray], NDArray] = colour_tag.value['func']

        if tag != 'RGB': 
            im = im.convert(tag)
        im = np.array(im, dtype = np.uint8)
        non_black_data = __process(im)
            
        data.append(non_black_data)
        
    return np.vstack(data)

def remove_outliers_iqr(data: NDArray) -> NDArray:
    """
    Remove outliers from data using IQR.
    Data points that fall below Q1 - 1.5 IQR or above the third quartile Q3 + 1.5 IQR are outliers.
    """
    Q1 = np.percentile(data, 25, axis=0)  # Calculate Q1 along columns (axis=0)
    Q3 = np.percentile(data, 75, axis=0)  # Calculate Q3 along columns (axis=0)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[((data >= lower_bound) & (data <= upper_bound)).all(axis=1)]  # Ensure 2D structure is preserved


def count(xyz_sk: NDArray) -> NDArray:
    """
    Return a frequency table of the integers in an input array
    """
    unique, counts = np.unique(xyz_sk, return_counts=True)
    freq = np.asarray((unique, counts)).T
    return freq