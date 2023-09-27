package server_components.db;
import java.io.File;
import java.sql.*;

import server_components.IO;


public class DatabaseManager {

    private static Connection conn;

    public static Connection getConn() {
        return conn;
    }

    public static void connect(boolean dropSchema) throws RuntimeException {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            // IO.serverMessage(String.format("Using:%nUser: %s%nPass: %s%n",ConfigManager.user, ConfigManager.pass));
            conn = DriverManager.getConnection("jdbc:MySQL://localhost:3306/weather", ConfigManager.user, ConfigManager.pass);
            applySchema(dropSchema);

            PreparedStatement st = conn.prepareStatement("USE weather");
            st.execute();
        } catch(ClassNotFoundException |SQLException e) {
            throw new RuntimeException(e.toString());
        }
    }

    private static void applySchema(boolean shouldDropSchema) throws RuntimeException {
        boolean exists = false;

        try (PreparedStatement st = conn.prepareStatement("SHOW DATABASES LIKE 'weather'")) {
            ResultSet result = st.executeQuery();
            exists = result.next();
            result.close();
        } catch (SQLException e) {
            throw new RuntimeException("Couldn't Run DB Query to find DB 'weather'.");
        }

        if (shouldDropSchema && exists) {
            try (PreparedStatement st = conn.prepareStatement("DROP DATABASE weather")) {
                st.execute();
            } catch (SQLException e) {
                throw new RuntimeException("Couldn't drop DB 'weather'");
            }
        }
        if (shouldDropSchema || !exists) {
            try {
                File schema = IO.locateFileRelativeToClass("schema.py", DatabaseManager.class);
                String path;

                if (schema != null) {
                    path = schema.getAbsolutePath();
                } else {
                    throw new RuntimeException("Schema definition not found.");
                }
                // pass the db credentials to the script
                new ProcessBuilder("python", path, ConfigManager.user, ConfigManager.pass, ConfigManager.host).inheritIO().start().waitFor();
            } catch (Exception e) {
                throw new RuntimeException("Couldn't load schema for Database: 'weather.'");
            }
        }

    }
}