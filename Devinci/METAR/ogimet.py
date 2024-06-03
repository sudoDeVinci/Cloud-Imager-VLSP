from Devinci.METAR.structs import *
from time import sleep
from sys import exit
from datetime import datetime, timedelta
from calendar import monthrange
import random

def random_datetimes(start_datetime, end_datetime, num_datetimes) -> List[datetime]:

    # Calculate the total time span between start_date and end_date
    total_seconds = (end_datetime - start_datetime).total_seconds()

    # Generate random datetimes with uniform distribution across the full range
    random_datetimes = []
    for _ in range(num_datetimes):
        # Generate a random number of seconds within the total time span
        random_seconds = random.uniform(0, total_seconds)

        # Calculate the corresponding random datetime
        random_dt = start_datetime + timedelta(seconds=random_seconds)

        # Append the random datetime to the list
        random_datetimes.append(random_dt)

    return random_datetimes

def daterange(start_date: datetime, end_date: datetime):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def _files_in_date_range(start_date_str, end_date_str, directory) -> List[str]:
    """_summary_

    Args:
        start_date_str (_type_): _description_
        end_date_str (_type_): _description_
        directory (_type_): _description_

    Returns:
        List[str]: _description_
    """
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    delta = timedelta(days=1)

    files_to_look_at = []

    current_date = start_date
    while current_date <= end_date:
        current_date_str = current_date.strftime('%Y-%m-%d')
        files = os.listdir(directory)
        for file in files:
            if file.endswith('.txt'):
                file_parts = file[:-4].split('-')  # Remove '.txt' and split filename by '-'
                file_start_date = datetime.strptime(file_parts[0], '%Y-%m-%d')
                file_end_date = datetime.strptime(file_parts[1], '%Y-%m-%d')
                if file_start_date <= current_date <= file_end_date:
                    files_to_look_at.append(os.path.join(file))

        current_date += delta

    return files_to_look_at
    
def get_measurement(path: str) -> List[Measurement]:
    """_summary_

    Args:
        path (str): _description_

    Returns:
        List[Measurement]: _description_
    """
    measurements = []

    # Check if cached readings exist.
    if not path.endswith(".txt"): return measurements
    cache_path = path.replace(".txt", ".pkl")
    cache_path = cache_path.replace(DATA_FOLDER, CACHE_FOLDER)
    debug(f"Cache: {cache_path}")
    
    if os.path.exists(cache_path):
        debug(f"Cache hit for {cache_path.replace(CACHE_FOLDER, "").replace(".txt", "")}")
        return unpickle_measurements(cache_path)

    # Open Metar file.
    data = load_data_file(path)
    if data is None: return measurements

    # Read each line as (timestamp, metar reading)
    metars = []
    for line in data:
        metar_code = line[13:].strip()
        stamp = line[0:12]
        if stamp == 'Fallo de con': continue
        t = datetime.strptime(stamp, '%Y%m%d%H%M')

        m = Metar.Metar(metarcode=metar_code, month=t.month, year=t.year, strict=False)
        if m.dewpt is None: continue
        if m.press is None: continue
        if m.temp is None: continue
        
        metars.append((m, t))
    
    measurements = [Measurement(m, t) for m, t in metars]
    
    # Cache measurements
    pickle_measurements(cache_path, measurements)

    return measurements


def get_all_measurements(port: Airport) -> List[Measurement]:
    """
    Get all METAR data in posession as a list of Measurements.
    """
    datapath = mkdir(os.path.join(DATA_FOLDER, port.value))
    measurements = []
    paths = tuple(p for p in os.listdir(datapath) if (p.endswith(".txt")))
    if not paths: return measurements
    start = paths[0].split("-")[0]
    end = paths[-1].split("-")[-1]

    # Check if cached readings exist.
    cache_folder = f"{mkdir(os.path.join(CACHE_FOLDER, port.value))}"
    cache_path = os.path.join(f"{cache_folder}",f"{start}-{end}").replace(".txt", ".pkl")
    if os.path.exists(cache_path):
        debug("Cache found!")
        return unpickle_measurements(cache_path) 
    
    # If cache miss, build array and re-cache.
    for name in paths:
        path = os.path.join(datapath, name)
        measurements.extend(get_measurement(path))

    # Cache measurements
    pickle_measurements(cache_path, measurements)
    
    return measurements

def ranged_query_ogimet(port: Airport, start: datetime, end: datetime) -> None:
    """_summary_

    Args:
        port (Airport): _description_
        start (datetime): _description_
        end (datetime): _description_
    """
    mkdir(f"{DATA_FOLDER}\\{port.value}")

    for year in range(start.year, end.year + 1):
        for month in range (1, 13):
            current_start = datetime(year=year, month=month, day=1)
            
            current_end = datetime(year=year, month=month, day=monthrange(year, month)[1])
            
            stamp = datetimes_to_timestamp(current_start, current_end)
            filepath = os.path.join(DATA_FOLDER, port.value, f'{stamp}.txt')

            if os.path.exists(filepath):
                print(f"{stamp} already exists.")
                continue

            print(f"getting {stamp}")
            data:str = query_ogimet(port, current_start, current_end)
            if data is None: continue
            with open(filepath, 'w') as f:
                f.write(data)
            sleep(15)


def query_ogimet(airport: Airport, start: datetime, end: datetime) -> str:
    """
    Returns the metar readings for the given time period.
    The first 11 lines are Comments specifying the:
    - Timestamp data
    - Airport Location (ICAO)
    - Altitude & GPS coords

    Each line after this is a METAR weather reading.
    ### Eg: 202206262020 METAR ESMX 262020Z 17004KT CAVOK 21/14 Q1018=
    """
    
    # Calculate the difference between start and end
    delta = end - start
    # Check if the difference is within 30 days
    if delta.days > 31:
        debug(f"METAR query time period exceeds 30 days.")
        return None
    
    # Get padded day, month, and year for start datetime
    start_day = f"{start.day:02d}"
    start_month = f"{start.month:02d}"
    start_year = f"{start.year:04d}"

    # Get padded day, month, and year for end datetime
    end_day = f"{end.day:02d}"
    end_month = f"{end.month:02d}"
    end_year = f"{end.year:04d}"

    #TODO: Bounds check for dates.

    url = f'https://www.ogimet.com/display_metars2.php?lang=en&lugar={airport.value}&tipo=ALL&ord=REV&nil=NO&fmt=txt&ano={start_year}&mes={start_month}&day={start_day}&hora=12&anof={end_year}&mesf={end_month}&dayf={end_day}&horaf=12&minf=59&send=send'
    reply = get(url)
    data = reply.content.decode(encoding = "utf-8").split('\n')
    data = tuple(f'{el}\n' for el in data)

    if len(data) <= 50: return None

    out = ""
    seen_num = False
    beg = 0

    for beg, line in enumerate(data[44:]): 
        if line in ('', ' ', '\n'): continue
        if line[0].isdigit():
            seen_num = True
            break  
    
    if seen_num is False: exit(1)

    out = f'{out}{''.join(data[39:50])}'

    for line in data[beg+44::]: 
        if line in ('', ' ', '\n'): continue
        if line[0] == '#': break
        out = f"{out}{line}"
    
    return out