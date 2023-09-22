import mysql.connector as mysql
import sys

# Establish the connection
try:
    mydb = mysql.connect(
        # read db creds from cli args
        user = sys.argv[1],
        password = sys.argv[2],
        host = sys.argv[3])

    print("successfully connected to the database")
        
except:
    print("\nconnection failed \ncheck host ip address and credentials")
    sys.exit()

# Define our cursor
myCursor = mydb.cursor()

# Create the cook book database 
myCursor.execute("CREATE DATABASE IF NOT EXISTS weather")

# Select the database
myCursor.execute("USE weather")

# Create the named device table
myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Devices(
        MAC VARCHAR(8) PRIMARY KEY,
        name VARCHAR(20),
        device_model VARCHAR(10),
        camera_model VARCHAR(10),
        altitude FLOAT(10) NOT NULL
    );
""")

# Create Readings table
myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Readings(
        MAC VARCHAR(8) PRIMARY KEY,
        temperature FLOAT(10) NOT NULL,
        relative_humidity FLOAT(10) NOT NULL,
        pressure FLOAT(10) NOT NULL,
        dewpoint FLOAT(10) NOT NULL,
        timestamp DATETIME,
        filepath VARCHAR(30)
    );
""")
                 
# Create status table
myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Status(
        MAC VARCHAR(8) PRIMARY KEY,
        is_up BOOLEAN NOT NULL
    );
""")


# Commit
mydb.commit()
print ("\n done! \n")
