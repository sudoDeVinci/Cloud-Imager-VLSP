import mysql.connector as mysql
from db.Entities import *
from db.Management import Manager
from analysis.config import debug
from typing import List
from abc import ABC


class Service(ABC):
    @staticmethod
    def get_all() -> List[Entity]:
        pass

    @staticmethod
    def get(MAC:str, *args) -> List[Entity]:
        pass

    @staticmethod
    def add(PK:str, *args) -> None:
        pass

    @staticmethod
    def update(PK:str, *args) -> None:
        pass

    @staticmethod
    def delete(PK:str, *args) -> None:
        pass

    @staticmethod
    def exists(PK:str) -> bool:
        pass


class DeviceService(Service):
    @staticmethod
    def get_all() -> List[DeviceEntity]:
        query_string = "SELECT * FROM Devices;"
        devices = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                device = DeviceEntity(
                    row["MAC"],
                    row["name"],
                    row["device_model"],
                    row["camera_model"],
                    row["altitude"],
                    row["latitude"],
                    row["longitude"]
                )
                devices.append(device)

        except mysql.Error as e:
            debug(f"Couldn't fetch device list -> {e}")

        finally:
            if cursor: cursor.close()

        return devices

    @staticmethod
    def get(MAC:str) -> DeviceEntity | None:
        query_string = "SELECT * FROM Devices WHERE MAC=%s LIMIT 1;"
        device = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC,))
            row = cursor.fetchone()
            if row:
                device = DeviceEntity(
                    row["MAC"],
                    row["name"],
                    row["device_model"],
                    row["camera_model"],
                    row["altitude"],
                    row["latitude"],
                    row["longitude"],
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch device list -> {e}")

        finally:
            if cursor: cursor.close()

        return device

    @staticmethod
    def add(MAC, name, dev_model, cam_model, altitude, latitude, longitude) -> None:
        conn = Manager.get_conn()

        # Insert records into the database.
        insert_string = "INSERT INTO Devices VALUES(%s, %s, %s, %s, %s, %s, %s);"

        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (MAC, name, dev_model, cam_model, altitude, latitude, longitude)
            )

            conn.commit()

        except mysql.connector.Error as e:
            debug(f"Couldn't insert device record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(MAC:str, name:str) -> None:
        conn = Manager.get_conn()
        update_string = "UPDATE Devices SET name=%s WHERE MAC=%s;";
        try:
            cursor = conn.cursor()
            cursor.execute(update_string, (name, MAC))
            conn.commit()
            #debug("Updated database record!")
        except mysql.Error as e:
            print(f"Couldn't update device name -> {e}")

        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def exists(MAC:str) -> bool:
        query_string = "SELECT * FROM Devices WHERE MAC=%s LIMIT 1;"

        # If no device is retrieved, return False.
        device:bool = False

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC,))
            device = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't check for existence of device record -> {e}")
            return False

        finally:
            if cursor: cursor.close()

        return device


class ReadingService:
    @staticmethod
    def get_all() -> List[ReadingEntity]:
        query_string = "SELECT * FROM Readings;"
        readings = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                reading = ReadingEntity(
                    row["MAC"],
                    row["temperature"],
                    row["relative_humidity"],
                    row["pressure"],
                    row["dewpoint"],
                    row["timestamp"],
                    row["filepath"]
                )
                readings.append(reading)

        except mysql.Error as e:
            debug(f"Couldn't fetch reading data list -> {e}")

        finally:
            if cursor: cursor.close()

        return readings

    @staticmethod
    def get(MAC:str, timetsamp:str) -> ReadingEntity | None:
        query_string = "SELECT * FROM Readings WHERE timestamp=%s AND MAC=%s LIMIT 1;"
        reading = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            row = cursor.fetchone()
            if row:
                reading = ReadingEntity(
                    row["MAC"],
                    row["temperature"],
                    row["relative_humidity"],
                    row["pressure"],
                    row["dewpoint"],
                    row["timestamp"],
                    row["filepath"]
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch reading records list -> {e}")

        finally:
            if cursor: cursor.close()

        return reading

    @staticmethod
    def add(MAC:str, temp:float, hum:float, pres:float, dew:float, timestamp:str, filepath:str = "") -> None:
        conn = Manager.get_conn()
        insert_string = "INSERT INTO Devices VALUES(%s, %s, %s, %s, %s, %s, %s);"
        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (timestamp, MAC, temp, hum, pres, dew, filepath)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert sensor reading record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(MAC:str, timestamp:str, filepath:str = ""):
        conn = Manager.get_conn()
        update_string = "UPDATE Readings SET filepath=%s WHERE MAC=%s AND timestamp=%s;"

        try:
            cursor = conn.cursor()
            cursor.execute(
                update_string, (filepath, MAC, timestamp)
            )

            conn.commit()
        
        except mysql.Error as e:
            debug(f"Couldn't update sensor reading record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def exists(MAC:str, timestamp:str) -> bool:
        query_string = "SELECT * FROM Readings WHERE timestamp=%s AND MAC=%s LIMIT 1;"
        reading:bool = False

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (timestamp, MAC)
            )

            reading = cursor.fetchone() is not None
            
        except mysql.Error as e:
            debug(f"Couldn't fetch reading records list -> {e}")

        finally:
            if cursor: cursor.close()

        return reading


class StatusService:
    @staticmethod
    def get_all() -> List[SensorEntity]:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT;"
        statuses = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                status = SensorEntity(
                    row["MAC"],
                    row["timestamp"],
                    row["SHT"],
                    row["BMP"],
                    row["CAM"],
                    row["WIFI"]
                )
                statuses.append(status)

        except mysql.Error as e:
            debug(f"Couldn't fetch sensor status records list -> {e}")

        finally:
            if cursor: cursor.close()

        return status

    @staticmethod
    def get(MAC:str, timetsamp:str) -> SensorEntity | None:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT 1;"
        status = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            row = cursor.fetchone()
            if row:
                status = SensorEntity(
                    row["MAC"],
                    row["timestamp"],
                    row["SHT"],
                    row["BMP"],
                    row["CAM"],
                    row["WIFI"]
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch reading records list -> {e}")

        finally:
            if cursor: cursor.close()

        return status

    @staticmethod
    def add(MAC:str, timestamp:str, sht:bool, bmp:bool, cam:bool, wifi:bool) -> None:
        conn = Manager.get_conn()
        insert_string = "INSERT INTO Devices VALUES(%s, %s, %s, %s, %s, %s);"
        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (MAC, sht, bmp, cam, wifi, timestamp)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert sensor status record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(MAC:str, timestamp:str, sht:bool, bmp:bool, cam:bool, wifi:bool = True):
        conn = Manager.get_conn()
        update_string = "UPDATE Status SET SHT=%s, BMP=%s, CAM=%s, WIFI=%s, timestamp=%s WHERE MAC=%s;"

        try:
            cursor = conn.cursor()
            cursor.execute(
                update_string, (sht, bmp, cam, wifi, timestamp, MAC)
            )

            conn.commit()
        
        except mysql.Error as e:
            debug(f"Couldn't update sensor status record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def exists(MAC:str, timetsamp:str) -> bool:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT 1;"
        stats:bool = False

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC,))

            stats = cursor.fetchone() is not None
            
        except mysql.Error as e:
            debug(f"Couldn't fetch sensor status records list -> {e}")

        finally:
            if cursor: cursor.close()

        return stats

