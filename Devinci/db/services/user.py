from Devinci.db.services.service import *


class UserService(Service):
    @staticmethod
    def get_all() -> List[UserEntity]:
        query_string = "SELECT * FROM Users;"
        users = []
        cursor = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return None
            cursor.execute(query_string)

            for row in cursor.fetchall():
                user = UserEntity(
                    id = row["ID"],
                    name = row["name"],
                    email = row["email"],
                    password = row['password'],
                    role = Role.match(row["role"])
                )
                users.append(user)

        except mysql.Error as e:
            debug(f"Couldn't fetch users record -> {e}")

        finally:
            if cursor: cursor.close()

        return users


    @staticmethod
    def get_user(userID: str) -> UserEntity | None:
        query_string = "SELECT * FROM Users WHERE ID=%s LIMIT 1;"
        user = None
        cursor = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return None
            cursor.execute(query_string, (userID, ))

            row = cursor.fetchone()
            if row:
                user = UserEntity(
                    id = userID,
                    name = row["name"],
                    email = row["email"],
                    password = row['password'],
                    role = Role.match(row["role"])
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch user record -> {e}")

        finally:
            if cursor: cursor.close()

        return user

    @staticmethod
    def get(email: str, password: str = None) -> UserEntity | None:
        query_string = "SELECT * FROM Users WHERE email=%s LIMIT 1;" if password is None else "SELECT * FROM Users WHERE email=%s AND password=%s LIMIT 1;"
        user = None
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return None
            
            if password is None:
                cursor.execute(query_string, (email, ))
            else:
                cursor.execute(query_string, (email, password))

            row = cursor.fetchone()
            if row:
                user = UserEntity(
                    id = row["ID"],
                    name = row["name"],
                    email = email,
                    password = row['password'],
                    role = Role.match(row["role"])
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch user record -> {e}")

        finally:
            if cursor: cursor.close()

        return user

    @staticmethod
    def add(name: str, email:str, password:str, role: Role) -> None:
        conn = Manager.get_conn()
        cursor = None
        if not conn:
                debug("No database connection.")
                return None

        # Insert records into the database.
        insert_string = "INSERT INTO Users VALUES(%s, %s, %s, %s, %s);"

        try:
            cursor = Manager.get_conn().cursor()
            cursor.execute(
                insert_string, (str(uuid4()), name, email, password, role.value)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert user record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(userID:str, name:str, email:str, password:str, role: Role) -> None:
        pass

    @staticmethod
    def delete() -> None:
        pass

    @staticmethod
    def exists(email:str, password: str = None) -> bool:
        query_string = "SELECT * FROM Users WHERE email=%s LIMIT 1;" if not password else "SELECT * FROM Users WHERE email=%s AND password=%s LIMIT 1;"
        user:bool = False
        cursor = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            if not cursor:
                debug("No database connection.")
                return False
            if not password:
                cursor.execute(query_string, (email, ))
            else:
                cursor.execute(query_string, (email, password))

            user = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch user record -> {e}")

        finally:
            if cursor: cursor.close()

        return user