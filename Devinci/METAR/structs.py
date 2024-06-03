from Devinci.config import Enum, functools, debug, Any, Tuple, List, ROOT, os, mkdir, dispatch
from typing import Iterable, Generator
from datetime import datetime, UTC
from numpy import percentile
from metar import Metar
from Devinci.analysis.LCL import Measurement
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import pickle
from requests import get

CACHE_FOLDER = mkdir(os.path.join(ROOT, 'METAR', 'cache'))
DATA_FOLDER = mkdir(os.path.join(ROOT, 'METAR', 'data'))
GRAPH_FOLDER = mkdir(os.path.join(ROOT, 'METAR', 'graphs'))

class Airport(Enum):
    """
    Airport names and equivalent METAR callsign.
    """
    VAXJO = "ESMX"
    ATLANTA = "KATL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, airport:str):
        """
        Match input string to airport callsign.
        """
        airport = airport.upper()
        for _, port_sign in cls.__members__.items():
            if airport == port_sign.value.upper(): return port_sign
        return cls.UNKNOWN

class Locale(Enum):
    """
    Lanuguage Locales for requesting data.
    """
    Deutsch = "de-DE"
    English = "en-US"
    Español = "es-ES"
    Français = "fr-FR"
    Italiano = "it-IT"
    Nederlands = "nl-NL"
    Polski = "pl-PL"
    Português = "pt-PT"
    中文 = "zh-CN"

def datetimes_to_timestamp(start: datetime, end: datetime) -> str:
    # Get padded day, month, and year for start datetime
    start_day = f"{start.day:02d}"
    start_month = f"{start.month:02d}"
    start_year = f"{start.year:04d}"

    # Get padded day, month, and year for end datetime
    end_day = f"{end.day:02d}"
    end_month = f"{end.month:02d}"
    end_year = f"{end.year:04d}"
    return f"{start_year}{start_month}{start_day}-{end_year}{end_month}{end_day}"
    

def timestamp_to_path(timestamp:str) -> str:
    """
    Convert a timestamp to format usable for path.
    """
    timestamp = timestamp.replace(" ", "-")
    timestamp = timestamp.replace(":", "-")
    return timestamp


def load_data_file(path: str) -> List[str]:
    data = None
    beg = 0
    seen_num = False
    out = []
    
    if not os.path.exists(path):
        debug(f"File: {path} does not exist.")
        return None

    with open(path, 'r') as file:
        data = tuple(line.replace('\n', '') for line in file.readlines())
    
    for beg, line in enumerate(data): 
        if line in ('', ' ', '\n', '#'): continue
        if line[0].isdigit():
            seen_num = True
            break

    if seen_num is False: return None

    for line in data[beg::]: 
        if line in ('', ' ', '\n'): continue
        if line[0] == '#': break
        out.append(line)
    
    return out

def unpickle_measurements(path: str) -> List[Measurement]:
    measurements = []
    if not os.path.exists(path): return measurements
    with open(path, 'rb') as f:
        measurements = pickle.load(f) # deserialize using load()
    
    return measurements

def pickle_measurements(path: str, measurements) -> None:
    with open(path, 'wb') as f:
        pickle.dump(measurements, f) # serialize using dump()


def IQR(data: Iterable[Measurement]) -> float:
    """
    Data points that fall below Q1 - 1.5 IQR or above the third quartile Q3 + 1.5 IQR are outliers.
    """
    debug(f"Length: {len(data)}")
    Q1 = percentile(data, 25)  # Calculate Q1 along columns (axis=0)
    Q3 = percentile(data, 75)  # Calculate Q3 along columns (axis=0)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (lower_bound, upper_bound)

def point_env_vis(airport: Airport, measurements: Iterable[Measurement]) -> Tuple[Figure, Any, str]:
    """
    Create and return a Graph of the LCL observations from a given Number of Measurement Objects.
    """
    def index(m:Measurement) -> float:
        o = abs(m.lcl_feet() - m.CEILING)/m.CEILING
        return o
    
    def ceil_gntr(measurements: Iterable[Measurement]) -> Generator[Measurement, None, None]:
        return (m for m in measurements if m.CEILING is not None and m.CEILING != 0 and m.HUMIDITY <= 0.8)


    # Need to perform a simple IQR for the outliers
    LB, UB = IQR([index(m) for m in ceil_gntr(measurements)])
    points_lcl = tuple(m for m in ceil_gntr(measurements) if (LB <= index(m) <= UB))

    hum = tuple(m.HUMIDITY for m in points_lcl)
    diffs = tuple(index(m) for m in points_lcl)
    
    lcl = tuple(m.lcl_feet() for m in points_lcl)
    heights = tuple(m.CEILING for m in points_lcl)

    beg = points_lcl[0].TIMESTAMP
    end = points_lcl[-1].TIMESTAMP

    if points_lcl[0].TIMESTAMP > points_lcl[-1].TIMESTAMP: 
        beg = points_lcl[0].TIMESTAMP
        end = points_lcl[-1].TIMESTAMP
    else:
        beg = points_lcl[-1].TIMESTAMP
        end = points_lcl[0].TIMESTAMP

    srt = f'{beg.year}-{str(beg.month).zfill(2)}-{str(beg.day).zfill(2)} {str(beg.hour).zfill(2)}:{str(beg.minute).zfill(2)}'
    stp = f'{end.year}-{str(end.month).zfill(2)}-{str(end.day).zfill(2)} {str(end.hour).zfill(2)}:{str(end.minute).zfill(2)}'

    period = f'{stp} to {srt}'

    del points_lcl

    fs = 10

    fig, axes = plt.subplots(nrows=2, ncols=1)
    fig.set_figheight(30)
    fig.set_figwidth(30)

    fig.suptitle(f'\nLCL Observations | {airport.value} | {period}\n', fontsize=fs*2)
    axes[0].scatter(hum, diffs, color = 'blue', alpha=0.4, s=10, label = 'LCL calculation fractional delta versus humidity')
    axes[0].set_xlabel("\nRel. Humidity\n", fontsize = fs)
    axes[0].set_ylabel("\nPredicted LCL Δ / Actual Cloud Base Height\n", fontsize = fs)
    axes[0].legend(loc='upper left', fancybox=True, shadow=True, ncol=1, fontsize = fs)
    axes[0].tick_params(axis='both', which='major', labelsize=fs)

    del hum, diffs

    axes[1].scatter(heights, lcl, color = 'purple', alpha = 0.6, s=10, label = 'LCL versus METAR Reported heights (feet)')
    axes[1].set_xlabel("\nMETAR Cloud Base Heights (feet)\n", fontsize = fs)
    axes[1].set_ylabel("\nPredicted LCL (feet)\n", fontsize = fs)
    axes[1].legend(loc='upper left', fancybox=True, shadow=True, ncol=1, fontsize = fs)
    axes[1].tick_params(axis='both', which='major', labelsize=fs)

    del heights, lcl

    fig.tight_layout(pad=1)
    return (fig, axes, timestamp_to_path(period))
