package server_components.db;
import java.io.File;
import java.sql.*;

import server_components.IO;


public class DatabaseManager {

    private static Connection conn;

    public static Connection getConn() {
        return conn;
    }

    public static void connect(boolean dropSchema) throws RuntimeException{
        try {
            conn = DriverManager.getConnection("jdbc:mysql://localhost", ConfigManager.user, ConfigManager.pass);
            applySchema(dropSchema);

            PreparedStatement st = conn.prepareStatement("USE weather");
            st.execute();
        } catch(SQLException e) {
            IO.errOut("Couldn't connect to database: ", e);
            throw new RuntimeException("Couldn't connect to Database, Please check config and network/database status.");
        }
    }

    private static void applySchema(boolean shouldDropSchema) {
        boolean exists = false;

        try (PreparedStatement st = conn.prepareStatement("SHOW DATABASES LIKE 'weather'")) {
            ResultSet result = st.executeQuery();
            exists = result.next();
            result.close();
        } catch (SQLException e) {
            System.out.println(e);
        }

        if (shouldDropSchema && exists) {
            try (PreparedStatement st = conn.prepareStatement("DROP DATABASE weather")) {
                st.execute();
            } catch (SQLException e) {
                System.out.println(e);
            }
        }
        if (shouldDropSchema || !exists) {
            try {
                File schema = IO.locateFileRelativeToClass("schema.py", DatabaseManager.class);
                String path;

                if (schema != null) {
                    path = schema.getAbsolutePath();
                } else {
                    IO.serverMessage(String.format("Schema definition not found."));
                    throw new RuntimeException();
                }
                // pass the db credentials to the script
                new ProcessBuilder("python", path, ConfigManager.user, ConfigManager.pass).inheritIO().start()
                        .waitFor();
            } catch (Exception e) {
                IO.errOut("Couldn't load schema for Database: ", e);
            }
        }

    }
}