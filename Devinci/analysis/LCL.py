"""
Version 1.0 released by David Romps on September 12, 2017.
Version 1.1 vectorized lcl.R, released on May 24, 2021.

Code from: https://romps.berkeley.edu/papers/pubs-2016-lcl.html

@article{16lcl,
   Title   = {Exact expression for the lifting condensation level},
   Author  = {David M. Romps},
   Journal = {Journal of the Atmospheric Sciences},
   Year    = {2017},
   Month   = dec,
   Number  = {12},
   Pages   = {3891--3900},
   Volume  = {74}
}
"""

from Devinci.config import debug, dispatch, datetime
from Devinci.db.Entities import ReadingEntity

from scipy.special import lambertw
from metar.Metar import Metar
from math import exp

class Measurement:
    """
    A Singular timestamped set of Environmental Measurements.
    This can be initilized via:
    - ReadingEntity
    - Metar Object
    - Manual Population
    """

    __slots__ = ('HUMIDITY', 'TEMPERATURE', 'DEWPOINT', 'PRESSURE', 'ALTITUDE', 'QNH', 'TIMESTAMP', 'CEILING', '_pvstarl_cached', '_pvstars_cached', 'Ttrip', 'ptrip', 'E0v', 'E0s', 'ggr', 'rgasa', 'rgasv', 'cva', 'cvv', 'cvl', 'cvs', 'cpa','cpv')

    # Environmental Reading Values
    HUMIDITY: float    # Rel Humidity percentagee, 0-1
    TEMPERATURE: float # Temperature in Celsius
    DEWPOINT: float    # Dewpoint in Celsius
    PRESSURE: float   # Pressure in Pa
    ALTITUDE: float    # Altitude from Seal level in Metres
    QNH: float         # Pressure at Sea Level in Pa
    TIMESTAMP: datetime   # Formatted UTC ISO Timestamp

    CEILING: float
    _pvstarl_cached:float
    _pvstars_cached:float

    @dispatch(float, float, float)
    def __init__(self, temp: float, hum: float, pressure: float) -> None:
        self._populate()
        self.TEMPERATURE = temp
        self.HUMIDITY = hum
        self.PRESSURE = pressure
        self.pvstarl()
        self.pvstars()


    @dispatch(float, float, float, float, float, float)
    def __init__(self, temp: float, hum: float, pressure: float,
                dewpoint: float, timestamp: str, altitude: float = None,
                qnh:float = None) -> None:
        self._populate()
        self.ALTITUDE = altitude
        self.DEWPOINT = dewpoint
        self.TEMPERATURE = temp
        self.HUMIDITY = hum
        self.QNH = qnh
        self.PRESSURE = pressure
        self.TIMESTAMP = timestamp

    @dispatch(ReadingEntity)
    def __init__(self, reading: ReadingEntity) -> None:
        self._populate()
        self.HUMIDITY = reading.get_humidity()
        self.PRESSURE = reading.get_pressure()
        self.DEWPOINT = reading.get_dewpoint()
        self.TEMPERATURE = reading.get_temperature()


    @dispatch(ReadingEntity, float)
    def __init__(self, reading: ReadingEntity, altitude: float) -> None: 
        self.ALTITUDE = altitude
        self.__init__(reading)


    @dispatch(Metar, datetime)
    def __init__(self, metar: Metar, timestamp: datetime) -> None:
        self._populate()
        self.TIMESTAMP = timestamp
        self.DEWPOINT = metar.dewpt.value("C")
        self.TEMPERATURE = metar.temp.value("C")
        self.PRESSURE = 100.0 * metar.press.value("HPA")
        self.HUMIDITY = self.__calc_rh(T = self.TEMPERATURE, Dp = self.DEWPOINT)
        self.CEILING = self.__parse_conditions(metar.sky_conditions())


    @dispatch(Metar, datetime, float)
    def __init__(self, metar: Metar, timestamp: datetime, qnh: float) -> None:
        self.__init__(metar, timestamp)
        self.QNH = qnh

    def _populate(self) -> None:
        # Universal Natural Constants
        self.Ttrip = 273.16          # K -------> Triple point temp of water
        self.ptrip = 611.657          # Pa ------> Triple point pressure of water vapour
        self.E0v   = 2.25e6        # J/kg ----> Latent heat of vaporization of water
        self.E0s   = 0.3337e6        # J/kg ----> Latent heat of sublimation of ice
        self.ggr   = 9.81       # m/s^2 ---> Acceleration due to gravity
        self.rgasa = 287.04          # J/kg/K --> Specific gas constant for dry air
        self.rgasv = 461             # J/kg/K --> Specific gas constant for water vapor
        self.cva   = 719             # J/kg/K --> Specific heat capacity of dry air at constant volume
        self.cvv   = 1418            # J/kg/K --> Specific heat capacity of water vapor at constant volume
        self.cvl   = 4119            # J/kg/K --> Specific heat capacity of liquid water at constant volume
        self.cvs   = 1861            # J/kg/K --> Specific heat capacity of solid ice at constant volume
        self.cpa   = self.cva + self.rgasa     # J/kg/K --> Specific heat capacity of dry air at constant pressure 
        self.cpv   = self.cvv + self.rgasv     # J/kg/K --> Specific heat capacity of water vapor at constant pressure
        self._pvstarl_cached:float = None
        self._pvstars_cached:float = None

    def __parse_conditions(self, phrase: str) -> float:
        """
        Return the lowest cloud layer given via the Metar.sky_conditions() method.
        """
        if phrase is None: return None
        if phrase == "": return None
        layers = phrase.split(";")

        heights = [float(layer.split(" ")[-2]) for layer in layers if "clear" not in layer and layer.split(" ")[-2].isdigit()]

        if not heights: return None
        height = min(heights)

        return height

    def __calc_rh(self, T: float, Dp: float) -> float:
        """
        As Relative humidity is not included in METAR readings, we derive it.
        Calculate relative humidity using the given temperature (T) and dew point (Dp).
    
        Arguments:
        T -- Temperature in degrees Celsius
        Dp -- Dew point in degrees Celsius
        
        Returns:
        Relative humidity in percentage
        """

        numerator = exp(17.625 * Dp / (243.04 + Dp))
        denominator = exp(17.625 * T / (243.04 + T))
        RH = numerator / denominator*1.0
        return RH
    
    @property
    def pvstarl(self) -> float:
        """
        The saturation vapor pressure over liquid water.
        """
        if self._pvstarl_cached is None:
            T = self.TEMPERATURE + 273.15
            self._pvstarl_cached = self.ptrip * (T/self.Ttrip)**((self.cpv-self.cvl)/self.rgasv) * \
                exp( (self.E0v - (self.cvv-self.cvl)*self.Ttrip) / self.rgasv * (1/self.Ttrip - 1/T) )
        return self._pvstarl_cached

    @property
    def pvstars(self) -> float:
        """
        The saturation vapor pressure over solid ice.
        """
        if self._pvstars_cached is None:
            T = self.TEMPERATURE + 273.15
            self._pvstars_cached = self.ptrip * (T/self.Ttrip)**((self.cpv-self.cvs)/self.rgasv) * \
                exp( (self.E0v + self.E0s - (self.cvv-self.cvs)*self.Ttrip) / self.rgasv * (1/self.Ttrip - 1/T) )
        return self._pvstars_cached 

    def __lcl(self, p:float, T:float, rh:float = None, rhl:float=None,
              rhs: float = None, return_ldl: bool = False, return_min_lcl_ldl: bool = False) -> float:
        """
        This lcl function returns the height of the lifting condensation level
        (LCL) in meters.  The inputs are:
        - p in Pascals
        - T in Kelvins
        - Exactly one of rh, rhl, and rhs (dimensionless, from 0 to 1):
            * The value of rh is interpreted to be the relative humidity with respect to liquid water if T >= 273.15 K and with respect to ice if T < 273.15 K. 
            * The value of rhl is interpreted to be the relative humidity with respect to liquid water
            * The value of rhs is interpreted to be the relative humidity with respect to ice
        - return_ldl is an optional logical flag.  If true, the lifting deposition level (LDL) is returned instead of the LCL. 
        - return_min_lcl_ldl is an optional logical flag.  If true, the minimum of the LCL and LDL is returned.
        """

        if return_ldl and return_min_lcl_ldl:
            debug('return_ldl and return_min_lcl_ldl cannot both be true')

        if (rh is None) and (rhl is None) and (rhs is None):
            debug('Error in lcl: Exactly one of rh, rhl, and rhs must be specified')
            return -1

        if rh is not None:
            pv = rh * self.pvstarl if T > self.Ttrip else rh * self.pvstars
            rhl = pv / self.pvstarl
            rhs = pv / self.pvstars
        elif rhl is not None:
            pv = rhl * self.pvstarl
            rhs = pv / self.pvstars
            rh = rhl if T > self.Ttrip else rhs
        elif rhs is not None:
            pv = rhs * self.pvstars
            rhl = pv / self.pvstarl
            rh = rhl if T > self.Ttrip else rhs

        if pv > p:
            debug('Error in lcl: pv greater than p')
            return -2

        qv = self.rgasa * pv / (self.rgasv * p + (self.rgasa - self.rgasv) * pv)
        rgasm = (1 - qv) * self.rgasa + qv * self.rgasv
        cpm = (1 - qv) * self.cpa + qv * self.cpv
        if rh == 0:
            return cpm * T / self.ggr

        aL = -(self.cpv - self.cvl) / self.rgasv + cpm / rgasm
        bL = -(self.E0v - (self.cvv - self.cvl) * self.Ttrip) / (self.rgasv * T)
        cL = pv / self.pvstarl * exp(-(self.E0v - (self.cvv - self.cvl) * self.Ttrip) / (self.rgasv * T))
        aS = -(self.cpv - self.cvs) / self.rgasv + cpm / rgasm
        bS = -(self.E0v + self.E0s - (self.cvv - self.cvs) * self.Ttrip) / (self.rgasv * T)
        cS = pv / self.pvstars * exp(-(self.E0v + self.E0s - (self.cvv - self.cvs) * self.Ttrip) / (self.rgasv * T))
        
        lcl = cpm * T / self.ggr * (1 - bL / (aL * lambertw(bL / aL * cL ** (1 / aL), -1).real))
        ldl = cpm * T / self.ggr * (1 - bS / (aS * lambertw(bS / aS * cS ** (1 / aS), -1).real))

        if return_ldl:
            return ldl
        elif return_min_lcl_ldl:
            return min(lcl, ldl)
        
        return lcl
    
    def lcl_meters(self) -> float:
        temp = self.TEMPERATURE + 273.15
        return self.__lcl(self.PRESSURE, temp, self.HUMIDITY)
    
    def lcl_feet(self) -> float:
        return self.lcl_meters() * 3.28084



if __name__ == "__main__":
    measure = Measurement(Metar("METAR ESMX 040150Z AUTO VRB05KT 9999 BKN013/// OVC023/// M01/M03 Q1011"),datetime.strptime('202404040016', '%Y%m%d%H%M'))
    print(f'{measure.lcl_feet()} feet LCL versus actual of {measure.CEILING}')