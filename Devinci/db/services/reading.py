from Devinci.db.services.service import *


class ReadingService(Service):
    @staticmethod
    def get_all() -> List[ReadingEntity]:
        query_string = "SELECT * FROM Readings;"
        readings = []
        cursor = None
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
    def get(MAC:str, timestamp:str) -> ReadingEntity | None:
        query_string = "SELECT * FROM Readings WHERE timestamp=%s AND MAC=%s LIMIT 1;"
        reading = None
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (timestamp, MAC)
            )

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
        insert_string = "INSERT INTO Readings VALUES(%s, %s, %s, %s, %s, %s, %s);"
        cursor = None
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
    def update_path(MAC:str, timestamp:str, filepath:str):
        conn = Manager.get_conn()
        update_string = "UPDATE Readings SET filepath=%s WHERE MAC=%s AND timestamp=%s;"
        cursor = None
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
    def update_readings(MAC:str, temp:float, hum:float, pres:float, dew:float, timestamp:str):
        conn = Manager.get_conn()
        update_string = "UPDATE Readings SET temperature=%s, relative_humidity=%s,pressure=%s,dewpoint=%s WHERE MAC=%s AND timestamp=%s;"
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                update_string, (temp, hum, pres, dew, MAC, timestamp)
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
        cursor = None
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
