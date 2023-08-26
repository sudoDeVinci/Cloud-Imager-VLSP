from machine import Pin, I2C
import sht31
import bmp390
from time import sleep_ms
from sensor_pack.bus_service import I2cAdapter

i2c = I2C(scl=Pin(26), sda=Pin(27), freq =400000)
sht_sensor = sht31.SHT31(i2c, addr=0x44)

i2c = I2C(scl=Pin(19), sda=Pin(18), freq=400000)
adaptor = I2cAdapter(i2c)
bmp390_sensor = bmp390.Bmp390(adaptor)
bmp390_sensor.set_oversampling(2, 3)
bmp390_sensor.set_sampling_period(5)
bmp390_sensor.set_iir_filter(2)
bmp390_sensor.start_measurement(True, True, 2)


"""
Convert air pressure from Pa to mm Hg.
"""
def pa_mmhg(value: float) -> float:
    if value is not None:
        value = value*7.50062E-3
    return value


"""
Return a tuple of the sht31 and bmp390 readings.
"""
def get_bmp_sht_readings() -> tuple[float,float,float,float,float]:
    bmp390_status = bmp390_sensor.get_status()
    if bmp390_status[2] and bmp390_status[1]:
        bmp390_temp, bmp390_pressure = bmp390_sensor.get_temperature(), bmp390_sensor.get_pressure()
    else:
        bmp390_temp, bmp390_pressure = None, None
         
    sht_temp, sht_hum = sht_sensor.get_temp_humi()
    
    if bmp390_temp is not None:
        dewpoint = bmp390_temp - ((100-sht_hum)/5)
    else:
        dewpoint = None  
    return (sht_temp, sht_hum, bmp390_temp, bmp390_pressure, dewpoint)


"""
Print formatted.
"""
def print_readings() -> None:
    sht_temp, sht_hum, bmp390_temp, bmp390_pressure, dewpoint = get_bmp_sht_readings()
    print(f"{sht_temp} \xB0C\t||\t{sht_hum}% Rh\n{bmp390_temp} \xB0C\t||\t{bmp390_pressure} hPa ({pa_mmhg(bmp390_pressure)} mm Hg)\nDew point: {dewpoint}\n")


"""
Only run constantly if run as main script.
"""
if __name__ == "__main__":
    while (True):
        print_readings()
        sleep_ms(800)  
