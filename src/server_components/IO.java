package server_components;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Class to handle IO, including FileIO
 */
public class IO {

    private String[] headers = {"image size","name", "temperature", "humidity", "pressure", "dewpoint"};
    private String[] units = {"bytes","","\u00B0C","% Rh","hPA","\u00B0C"};
    /**
     * 
     */
    public String[] getHeaders() {
        return headers;
    }

    /**
     * Print a stylized usage message. 
    */
    public void printUsage() {
        System.err.println("Usage: java Server <port>");
    }


    /**
     * Ensure a folder for readings/images exists
     * @param path Path to folder
     */
    public void ensureFolderExists(String path) {
        Path folder = Paths.get(path);
        if (Files.exists(folder) && Files.isDirectory(folder)) {
           return;
        }

        try {
            Files.createDirectories(folder);
        } catch (IOException e) {
            errOut("Error creating folder: ", e);
        }
    }

    /**
     * Write jpeg image from buffer. Return true/false.
     * @param imageLength Lenght of image buffer in bytes
     * @param imageName Path to image
     * @param buffer Image byte buffer
     * @return
     */
    public void writeImage(int imageLength, String imageName, byte[] buffer) {
        try {
            FileOutputStream fileOutputStream = new FileOutputStream(imageName);
            fileOutputStream.write(buffer);
            fileOutputStream.close();
            serverMessage("Image saved as: " + imageName);
        } catch (Exception err) {
            errOut("Couldn't save image " + imageName, err);
            // TODO: write to error logs.
        }
    }

    /**
     * Write Sensor readings to a csv file.
     * @param content Readings
     * @param path path to csv file
     */
    public void writeReadings(String[] content, String path, String datestamp, String timestamp) {
        try (FileWriter writer = new FileWriter(path)){
            for (int i = 1; i<headers.length;i++) {
                writer.append(headers[i]);
                writer.append(',');
            }
            writer.append('\n');

            // Write data
            for (int i =1; i<content.length;i++) {
                writer.append(content[i]);
                writer.append(',');
            }
            serverMessage("Readings saved as: " + path);
        } catch (IOException err) {
             errOut("Couldn't save readings: ", err);
        }
    }

    /**
     * Write the rrror to the logs for today with a timestamp.
     * @param num
     */
    private void writeError(String datestamp, String timestamp, String err) {
        // TODO
    }


    /**
     * Validate string is an int with given bounds.
     * Alias given to number for printout.
     * @param num
     * @param lb lower bound
     * @param ub upper bound
     * @param alias alias to call string in printouts
     * @return
     */
    public int stringToBoundedInt(String num, int lb, int ub, String alias) {
        int port;
        try {
            port = Integer.parseInt(num);
            if (port < lb || port > ub) {
                throw new IllegalArgumentException(" ");
            }
        } catch (NumberFormatException e) {
            System.err.println("Invalid " + alias + " number: " + num);
            port = -1;
        } catch (IllegalArgumentException e) {
            System.err.println(alias + " number must be between " + lb + " and " + ub);
            port = -1;
        }    

        return port;
    }

    /**
     * Convert a string to a positive integer.
     * If negative, or not an int, return -1
     * @param str String to convert
     * @return -1 or integer.
     */
    public int stringToInt(String str) {
        int num;
        try {
            num = Integer.parseInt(str);
            if (num < 0) {
                num = -1;
            }
        } catch (NumberFormatException e) {
            // System.err.println("Invalid number: " + str);
            num = -1;
        }
        return num;
    }

    /**
     * Convert a string to a positive floating point.
     * If negative, or not a float, return -1
     * @param str String to convert
     * @return -1 or float.
     */
    public float stringToFloat(String str) {
        float num;
        try {
            num = Float.parseFloat(str);
            if ( num < 0) {
                num = -1;
            }
        } catch (NumberFormatException e) {
            //System.err.println("Invalid number: " + str);
            num = -1;
        }
        return num;
    }

    /**
     * Print stylized server event message.
     * @param messageMessage to print
     */
    public static void serverMessage(String message) {
        System.out.println(message);
    }


    /**
     * Print stylized errors to user.
     * @param err Error to stylize.
     */
    public static void loggedErrOut(String message, Exception err, String datestamp, String timestamp) {
        System.out.print(message);
        System.out.println(err.getMessage());
        //TODO: write error.
    }

     /**
     * Print stylized errors to user.
     * @param err Error to stylize.
     */
    public static void errOut(String message, Exception err) {
        System.out.print(message);
        System.out.println(err.getMessage());
    }


    /**
     * Printout of a packet's content.
     * It is assumed the packet is in the correct format.
     * @param addr The address of the client the packet was received from
     * @param packetHeaders The String list of the packet header content
     */
    public void displayPacket(String addr, String[] packetHeaders) {
        String separator = "------------------------------";
        
        serverMessage(separator);
        serverMessage("FROM " + addr);
        serverMessage(separator);
        for (int i = 0; i < headers.length; i++) {
            packetHeaders[i] = packetHeaders[i].replace("[", "").replace("]","");
            serverMessage(headers[i] + " : " + packetHeaders[i] + " " + units[i]);
        }
        serverMessage(separator);
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
