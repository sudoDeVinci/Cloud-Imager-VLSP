package server_components.db;
import java.io.File;
import java.util.Map;
import server_components.IO;

import server_components.db.parser.Toml;

/**
 * This attempts to load the config file of the database 'weather'.
 */
public class ConfigManager {
    public static String host;
    public static String pass;
    public static String user;
    public static long port;
    public static String tomlPath;

    /**
     * Load the config from toml and populate the ConfigManager object.
     */
    public static void load() {
        try {
            File configFile = IO.locateFileRelativeToClass("configs/db_cfg.toml", ConfigManager.class);
            if (configFile != null) {
                tomlPath = configFile.getAbsolutePath();
                System.out.println("Config file located at: " + tomlPath);
            } else {
                System.out.println("Config file not found.");
                throw new RuntimeException();
            }
            
            Map<String, Map<String, Object>> tomlData = Toml.parse(tomlPath);
            Map<String, Object> mysqlConfig = tomlData.get("mysql");
            // Extract and initialize the static fields
            host = (String) mysqlConfig.get("host");
            pass = (String) mysqlConfig.get("password");
            user = (String) mysqlConfig.get("user");
            port = (long) mysqlConfig.get("port");
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("NAH");
        }
    }


}
