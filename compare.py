from Devinci.METAR.ogimet import *
from matplotlib.dates import date2num
from Devinci.db.services.reading import ReadingService
    
port = Airport.VAXJO
mkdir(os.path.join(DATA_FOLDER, port.value))
mkdir(os.path.join(CACHE_FOLDER, port.value))
graphdir = mkdir(os.path.join(GRAPH_FOLDER, port.value))

start = datetime(year=2024, month=5, day=1)
end = datetime(year=2024, month=5, day=14)

readings = get_measurement(os.path.join(DATA_FOLDER, port.value, "20240501-20240514.txt"))
metar_dates = [date2num(reading.TIMESTAMP) for reading in readings]
metar_date_strs = [reading.TIMESTAMP.strftime("%m-%d %H:%M:%S") for reading in readings]
metar_hums = [reading.HUMIDITY for reading in readings]
metar_temps = [reading.TEMPERATURE for reading in readings]
metar_press = [reading.PRESSURE for reading in readings]



station_readings = ReadingService.get_all()
station_dates = [date2num(reading.timestamp) for reading in station_readings]
station_dates_str = [reading.timestamp.strftime("%m-%d %H:%M:%S") for reading in station_readings]
station_hums = [reading.get_humidity() for reading in station_readings]
station_temps = [reading.get_temperature() for reading in station_readings]
station_press = [reading.get_pressure() for reading in station_readings]

plt.rcParams["figure.autolayout"] = True
bg_color = '#f0f0f0'
line_color = "#202330"
fs = 10
fig, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols = 1)
    
    
ax0.spines['top'].set_linewidth(0)
ax0.spines['left'].set_linewidth(2)
ax0.spines['right'].set_linewidth(0)
ax0.spines['bottom'].set_linewidth(2)

ax1.spines['top'].set_linewidth(0)
ax1.spines['left'].set_linewidth(2)
ax1.spines['right'].set_linewidth(0)
ax1.spines['bottom'].set_linewidth(2)

ax2.spines['top'].set_linewidth(0)
ax2.spines['left'].set_linewidth(2)
ax2.spines['right'].set_linewidth(0)
ax2.spines['bottom'].set_linewidth(2)

fig.set_figheight(360)
fig.set_figwidth(60)
fig.set_facecolor(bg_color)
ax0.set_facecolor(bg_color)
ax1.set_facecolor(bg_color)
ax2.set_facecolor(bg_color)

ax0.set_title(f"\n\nMETAR Reported versus Station Observed Relative Humidities\n",loc='center', fontsize = fs*1.25)
ax0.plot(metar_dates, metar_hums,'blue', label = "METAR Reported Humidities")
ax0.set_xlabel("\nDates\n", loc='center', fontsize = fs)
ax0.set_ylabel("\nRel. Humidity\n", fontsize = fs)
ax0.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, fontsize = fs, edgecolor = "#202330", labelcolor = "#202330", framealpha = 0.8, prop = {'weight':'bold', 'size':fs})
ax0.tick_params(axis='both', which='major', labelsize=fs, width = 2)
ax0.set_xticklabels(metar_date_strs)

ax1.set_title(f"\n\nMETAR Reported versus Station Observed Temperatures (C)\n",loc='center', fontsize = fs*1.25)
ax1.plot(metar_dates, metar_temps,'green', label = "METAR Reported Temperatures")
ax1.set_xlabel("\nDates\n", loc='center', fontsize = fs)
ax1.set_ylabel("\nTemperatures\n", fontsize = fs)
ax1.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, fontsize = fs, edgecolor = "#202330", labelcolor = "#202330", framealpha = 0.8, prop = {'weight':'bold', 'size':fs})
ax1.tick_params(axis='both', which='major', labelsize=fs, width = 2)
ax1.set_xticklabels(metar_date_strs)

ax2.set_title(f"\n\nMETAR Reported versus Station Observed Air Pressures (Pa)\n",loc='center', fontsize = fs*1.25)
ax2.plot(metar_dates, metar_press,'red', label = "METAR Reported Air Pressure")
ax2.set_xlabel("\nDates\n", loc='center', fontsize = fs)
ax2.set_ylabel("\nAir Pressure\n", fontsize = fs)
ax2.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, fontsize = fs, edgecolor = "#202330", labelcolor = "#202330", framealpha = 0.8, prop = {'weight':'bold', 'size':fs})
ax2.tick_params(axis='both', which='major', labelsize=fs, width = 2)
ax2.set_xticklabels(metar_date_strs)


plt.show()

# plt.savefig(f"{os.path.join(graphdir, stamp)}.png")
# plt.clf()