from Devinci.db.services.service import *


class LocationService(Service):
    @staticmethod
    def country_exists(region:str) -> bool:
        query_string = "SELECT * FROM Locations WHERE country=%s;"
        location = False
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return False
            cursor.execute(
                query_string, (region, )
            )

            location = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch country location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location

    @staticmethod
    def region_exists(region:str) -> bool:
        query_string = "SELECT * FROM Locations WHERE region=%s;"
        location = False
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return False
            cursor.execute(
                query_string, (region, )
            )

            location = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch region location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location


    @staticmethod
    def city_exists(city:str) -> bool:
        query_string = "SELECT * FROM Locations WHERE city=%s;"
        location = False
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return False
            cursor.execute(
                query_string, (city, )
            )

            location = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch city location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location

    @staticmethod
    def exists(latitude:float, longitude:float) -> bool:
        query_string = "SELECT * FROM Locations WHERE latitude=%s AND longitude=%s LIMIT 1;"
        location = False
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return False
            cursor.execute(
                query_string, (latitude, longitude)
            )

            location = cursor.fetchone() is not None
        
        except mysql.Error as e:
            debug(f"Couldn't fetch location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location
        

    @staticmethod
    def get_all() -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations;"
        locs = []
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return []
            cursor.execute(query_string)

            for row in cursor.fetchall():
                location = LocationEntity(
                    row["country"],
                    row["region"],
                    row["city"],
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs

    def get(latitude:float, longitude:float) -> LocationEntity:
        query_string = "SELECT * FROM Locations WHERE latitude=%s AND longitude=%s LIMIT 1;"
        location = None
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return None
            cursor.execute(
                query_string, (latitude, longitude)
            )

            row = cursor.fetchone()
            if row:
                location = LocationEntity(
                    row["country"],
                    row["region"],
                    row["city"],
                    latitude,
                    longitude
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location
    
    def get_city(city:str) -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations WHERE city=%s;"
        locs = []
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return []
            cursor.execute(
                query_string, (city, )
            )

            for row in cursor.fetchall():
                location = LocationEntity(
                    row["country"],
                    row["region"],
                    city,
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch city location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs
        
    def get_region(region:str) -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations WHERE region=%s;"
        locs = []
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return []
            cursor.execute(
                query_string, (region, )
            )

            for row in cursor.fetchall():
                location = LocationEntity(
                    row["country"],
                    region,
                    row["city"],
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch region location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs

    def get_country(country:str) -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations WHERE country=%s;"
        locs = []
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return []
            cursor.execute(
                query_string, (country, )
            )

            for row in cursor.fetchall():
                location = LocationEntity(
                    country,
                    row["region"],
                    row["city"],
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch country location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs