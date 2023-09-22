package server_components.db;
import java.io.File;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Path;
import java.util.Map;

import server_components.db.parser.Toml;

/**
 * This attempts to load the config file of the database 'weather'.
 */
public class ConfigManager {
    public final String host;
    public final String pass;
    public final String user;
    public final long port;
    public final String tomlPath;

    /**
     * load the config from toml and populate the ConfigManager object.
     */
    public ConfigManager() {
        try {
            File configFile = locateFileRelativeToClass("configs/db_cfg.toml", ConfigManager.class);
            if (configFile != null) {
                this.tomlPath = configFile.getAbsolutePath();
                System.out.println("Config file located at: " + tomlPath);
            } else {
                System.out.println("Config file not found.");
                throw new RuntimeException();
            }
            
            Map<String, Map<String, Object>> tomlData = Toml.parse(tomlPath);
            Map<String, Object> mysqlConfig = tomlData.get("mysql");
            // Extract and initialize the final fields
            this.host = (String) mysqlConfig.get("host");
            this.pass = (String) mysqlConfig.get("password");
            this.user = (String) mysqlConfig.get("user");
            this.port = (long) mysqlConfig.get("port");
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("NAH");
        }
    }

    public static File locateFileRelativeToClass(String relativePath, Class<?> clazz) {
        // Use the class's class loader to get the resource URL
        URL url = clazz.getResource(relativePath);

        if (url != null) {
            try {
                // Convert the URL to a file path
                return new File(url.toURI());
            } catch (URISyntaxException e) {
                e.printStackTrace();
            }
        }
        // Return null if the file cannot be located
        return null; 
    }
}
