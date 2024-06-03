from Devinci.db.services.service import *

class DeviceService(Service):
    @staticmethod
    def get_all() -> List[DeviceEntity]:
        query_string = "SELECT * FROM Devices;"
        devices = []
        cursor = None
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
        cursor = None
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
        cursor = None
        # Insert records into the database.
        insert_string = "INSERT INTO Devices VALUES(%s, %s, %s, %s, %s, %s, %s);"

        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (MAC, name, dev_model, cam_model, altitude, latitude, longitude)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert device record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(MAC:str, name:str) -> None:
        conn = Manager.get_conn()
        update_string = "UPDATE Devices SET name=%s WHERE MAC=%s;"
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(update_string, (name, MAC))
            conn.commit()
            #debug("Updated database record!")
        except mysql.Error as e:
            debug(f"Couldn't update device name -> {e}")

        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def exists(MAC:str) -> bool:
        query_string = "SELECT * FROM Devices WHERE MAC=%s LIMIT 1;"
        cursor = None
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