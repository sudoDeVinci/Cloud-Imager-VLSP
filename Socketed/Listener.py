import csv
from multiprocessing.connection import Client
from socket import *
from client import Listener
from datetime import datetime
import os

"""
Error logging for data retreival
"""
def logErr(err: Exception,subfolder:str, datestamp:str, timestamp:str):
     # If error log folder does not exist, create it
    if not os.path.exists(f"/Errors/{subfolder}/{datestamp}"):
        os.mkdir(f"/Errors/{subfolder}/{datestamp}")

    # Write error to text file
    with open(f"/Errors/{subfolder}/{datestamp}/{timestamp}.txt") as f:
        f.write(str(err))


"""
Listener server for testing.
Takes in a socket and listens for connections.
"""
def listen(sock: socket) ->None:
    while True:
        print("Listening...")
        conn, addr = sock.accept()
        datestamp = str(datetime.now().strftime("%Y%m%d"))
        timestamp = str(datetime.now().strftime("%H%M%S"))
        with Listener(conn) as l:
            # Show connection for debugging
            print('Connection from {0}'.format(str(addr)))

            # If datestamped folder does not exist, create it
            if not os.path.exists(f"images/{datestamp}"):
                os.mkdir(f"images/{datestamp}")
            
            # If datestamped folder does not exist, create it
            if not os.path.exists(f"readings/{datestamp}"):
                os.mkdir(f"readings/{datestamp}")

            # Attempt to receive image and write image to file.
            print("Receiving Image...")
            try:
                data = l.get()
                if data:
                    print("\t└ Image Received.")
                    with open(f"images/{datestamp}/img{timestamp}.png", 'wb')as f:
                        f.write(data)
                else:
                    print("\t└ NO Image Received.")

            except Exception as e:
                print(e)
                logErr(e, datestamp, timestamp)
                if conn:
                    conn.close()
            
            # Attempt to get weather data and write to file.
            # Define headers for the csv file format.
            # Readings are encoded as csv with '|' delimiter.
            headers = ["sht_temp_celsius", "sht_hum_percent", "bmp390_temp_celsius", "bmp390_pressure_hPa", "dewpoint_celsius"]
            print("Receiving Sensor Data...")
            try:
                data = l.get()
                if data:
                    print("\t├ Sensor Data Received.")
                    readings = data.decode('utf-8').split("|")
                    print(f"\t└ {readings}")
                    with open(f"readings/{datestamp}/{timestamp}.csv", 'wb', encoding = 'UTF-8', newline = '') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerow(readings)

            except Exception as e:
                print(e)
                logErr(e, datestamp, timestamp)
                if conn:
                    conn.close()


def main() -> None:
    # If content folders do not exist, create them
    if not os.path.exists(f"images/"):
        os.mkdir(f"images")
    if not os.path.exists(f"readings/"):
        os.mkdir(f"readings")
    if not os.path.exists(f"Errors/"):
        os.mkdir(f"Errors")
        

    sock = socket()
    ip = gethostbyname(getfqdn())
    print(ip)
    try:
        # Try to let the socket address be reusable
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # Try to bind the socket to an address and port
        sock.bind(('',88))
        sock.listen(100)
        # Listen, looping repeatedly
        listen(sock)
    except Exception as err:
        print(err)
        """
        Extra timestamp incase 
        """
        datestamp = str(datetime.now().strftime("%Y%m%d"))
        timestamp = str(datetime.now().strftime("%H%M%S"))
        logErr(err, datestamp, timestamp)
        if sock:
            sock.close()


if __name__ == '__main__':
    main()
