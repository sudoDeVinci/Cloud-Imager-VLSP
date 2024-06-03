import mysql.connector as mysql
import sqlite3 as sqlite

def apply(mydb:mysql.MySQLConnection | sqlite.Connection):

    print("Here")
    
    cursor: mysql.MySQLCursor |sqlite.Cursor = mydb.cursor()

    match type(mydb):
        case mysql.MySQLConnection:
            _apply_mysql(cursor)
        case sqlite.Connection:
            _apply_sqlite(cursor)
        case _:
            pass

    # Commit
    mydb.commit()

def _apply_sqlite(myCursor: sqlite.Cursor) -> None:

    # Create the Devices table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Devices(
            MAC TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            device_model TEXT NOT NULL,
            camera_model TEXT NOT NULL,
            altitude REAL NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        );
    """)

    # Create the Readings table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Readings(
            timestamp TEXT,
            MAC TEXT,
            temperature REAL,
            relative_humidity REAL,
            pressure REAL,
            dewpoint REAL,
            filepath TEXT,
            PRIMARY KEY (MAC, timestamp),
            FOREIGN KEY (MAC) REFERENCES Devices(MAC)
        );
    """)

    # Create the Status table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Status(
            MAC TEXT PRIMARY KEY,
            SHT INTEGER NOT NULL,
            BMP INTEGER NOT NULL,
            CAM INTEGER NOT NULL,
            WIFI INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (MAC) REFERENCES Devices(MAC)
        );
    """)

    # Create the Locations table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Locations(
            country TEXT,
            region TEXT,
            city TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            PRIMARY KEY (latitude, longitude)
        );
    """)

    # Create the Users table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            ID TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
    """)


def _apply_mysql(myCursor) -> None:
    # Create the cook book database 
    myCursor.execute("CREATE DATABASE IF NOT EXISTS weather")

    # Select the database
    myCursor.execute("USE weather")

    # Create the named device table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Devices(
            MAC VARCHAR(25) PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            device_model VARCHAR(10) NOT NULL,
            camera_model VARCHAR(10) NOT NULL,
            altitude FLOAT(10) NOT NULL,
            latitude FLOAT(10) NOT NULL,
            longitude FLOAT(10) NOT NULL
        );
    """)

    # Create readings table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Readings(
        timestamp DATETIME,
        MAC VARCHAR(25),
        temperature FLOAT(10),
        relative_humidity FLOAT(10),
        pressure FLOAT(10),
        dewpoint FLOAT(10),
        filepath VARCHAR(100),
        PRIMARY KEY (MAC, timestamp),
        FOREIGN KEY (MAC) REFERENCES Devices(MAC)
    );
""")
                    
    # Create status table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Status(
            MAC VARCHAR(25) PRIMARY KEY,
            SHT BOOLEAN NOT NULL,
            BMP BOOLEAN NOT NULL,
            CAM BOOLEAN NOT NULL,
            WIFI BOOLEAN NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (MAC) REFERENCES Devices(MAC)
        );
    """)

    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Locations(
            country VARCHAR(30),
            region VARCHAR(30),
            city VARCHAR(30),
            latitude FLOAT(10) NOT NULL,
            longitude FLOAT(10) NOT NULL,
            PRIMARY KEY (latitude, longitude)
        );
    """)

    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            ID VARCHAR(64) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(300) NOT NULL,
            role VARCHAR(30) NOT NULL
        );
    """)
