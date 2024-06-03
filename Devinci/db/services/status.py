from Devinci.db.services.service import *


class StatusService(Service):
    @staticmethod
    def get_all() -> List[SensorEntity]:
        query_string = "SELECT * FROM Status;"
        statuses = []
        cursor = None
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
    def get(MAC:str) -> SensorEntity | None:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT 1;"
        status = None
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC, ))

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
    def add(MAC:str, timestamp:str, sht:bool, bmp:bool, cam:bool, wifi:bool = True) -> None:
        conn = Manager.get_conn()
        insert_string = "INSERT INTO Status VALUES(%s, %s, %s, %s, %s, %s);"
        cursor = None
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
    def update(MAC:str, timestamp:str, sht:bool, bmp:bool, cam:bool, wifi:bool = True) -> None:
        conn = Manager.get_conn()
        cursor = None
        if not conn:
            debug("No database connection.")
            return None
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
    def exists(MAC:str) -> bool:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT 1;"
        stats:bool = False
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return False
            cursor.execute(query_string, (MAC,))

            stats = cursor.fetchone() is not None
            
        except mysql.Error as e:
            debug(f"Couldn't fetch sensor status records list -> {e}")

        finally:
            if cursor: cursor.close()

        return stats