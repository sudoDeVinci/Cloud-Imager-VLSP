package server_components.db.parser;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 
 */

public class Toml {

    public static Map<String, Map<String, Object>> parse(String filePath) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filePath));
        Map<String, Map<String, Object>> tomlData = new HashMap<>();
        String currentSection = null;

        String line;
        while ((line = reader.readLine()) != null) {
            // Check for sections like [section_name]
            if (line.matches("\\[.*\\]")) {
                currentSection = line.substring(1, line.length() - 1);
                tomlData.put(currentSection, new HashMap<>());
            } else {
                // Process key-value pairs within a section
                if (currentSection != null) {
                    String[] parts = line.split("=", 2);
                    if (parts.length == 2) {
                        String key = parts[0].trim();
                        String value = parts[1].trim();
                        ((Map<String, Object>) tomlData.get(currentSection)).put(key, parseValue(value));
                    }
                }
            }
        }

        reader.close();
        return tomlData;
    }

    private static Object parseValue(String value) {
        value = value.trim();
        if (value.startsWith("\"") && value.endsWith("\"")) {
            return value.substring(1, value.length() - 1);
        } else if (value.equalsIgnoreCase("true")) {
            return true;
        } else if (value.equalsIgnoreCase("false")) {
            return false;
        } else {
            try {
                return Long.parseLong(value);
            } catch (NumberFormatException e1) {
                try {
                    return Double.parseDouble(value);
                } catch (NumberFormatException e2) {
                    return value;
                }
            }
        }
    }
}
