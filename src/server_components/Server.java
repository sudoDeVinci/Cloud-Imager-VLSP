package server_components;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import server_components.exceptions.*;

/**
 * A simple TCP Server to accept multithreaded local connections from ESP32s running the Weather station software.
 * Packets are in the format [Size]#[Name]#[Temperature]#[Humidity]#[Pressure]#[Dewpoint]XX
 */
public class Server {
    IO io;
    int port;
    final int MAX_CONNECTIONS = 4;

    public Server(IO io, int port) {
        this.io = io;
        this.port = port;
        io.ensureFolderExists("images/");
        io.ensureFolderExists("readings/");
    }

    /**
     * A reliable way to get the current Network interface IPv4 address.
     * This solution is windows-only.
     * @return The ip address of the machine.
     */
    private String getLocalIP() {
        String ip = "";
        try(final DatagramSocket socket = new DatagramSocket()){
            socket.connect(InetAddress.getByName("8.8.8.8"), 10002);
            ip = socket.getLocalAddress().getHostAddress();
        } catch(Exception e) {
            IO.errOut("Couldn't get local ip: ", e);
        }
        return ip;
    }


    /*
     * Main runtime loop for socket server.
     * Each connection is handed to the clientHandler() on a separate thread and submitted
     * to the  threadpool.
     */
    public void start() {
        ExecutorService threads = Executors.newFixedThreadPool(MAX_CONNECTIONS);

        String ip = getLocalIP();
        
        try (ServerSocket serverSocket = new ServerSocket()) {
            serverSocket.bind(new InetSocketAddress(ip, port));
            System.out.println("Listening on: " + serverSocket.getInetAddress()+":"+serverSocket.getLocalPort());
            while (true){
                try {
                    Socket client = serverSocket.accept();
                    threads.submit(() -> {clientHandler(client);});
                } catch (Exception e){
                    IO.errOut("Unable to Submit socket to threadpool: ", e);
			    }
            }
        } catch (IOException e) {
            IO.errOut("Error starting server: ", e);
        } finally {
            threads.shutdown();
        }
    }


    /**
     * Validate the packet. Return the size of the image buffer.
     * @param headers The packet data as a string array.
     * @return The Length of the image buffer. If no image received, or error with the image, return 0.
     */
    private int validatePacket(String[] headers) throws MalformedPacketException, ImageBufferException{
        /**
         * If headers malformed, exit as-is.
         */
        if (headers.length != 6) {
            throw new MalformedPacketException("Packet ");
        }

        /**
         * Build a string of errors checking the type of headers.
         */
        String[] expectedHeaders = io.getHeaders();
        StringBuilder errors = new StringBuilder();

        for (int i = 2; i < headers.length; i++) {
            float value = io.stringToFloat(headers[i]);
            if (value == -1) {
                errors.append(String.format("%s has incompatible non-float value '%s%n'",expectedHeaders[i],headers[i]));
            }
        }

        if (!errors.isEmpty()) {
            throw new MalformedPacketException(errors.toString());
        }

        /**
        * Get length of image buffer.
        * If not an integer, exit & close conection. Throw error.
        * If the image length is 0, don't write image buffer to file. Throw error.
        */
        int imageLength = io.stringToInt(headers[0]);
        if (imageLength == -1) {
            throw new ImageBufferException("Got malformed packet length '"+headers[0]+"'.");
        } else if (imageLength == 0) {
            throw new ImageBufferException("No image received.");
        }

        return imageLength;
    }

    /**
     * Handler for each connection, handled on a separate thread.
     * A socket is passed and analyzed.
     * @param client
     */
    private void clientHandler(Socket client) {
        /**
         * Client connection input stream.
         */
        InputStream in;
        
        try {
            String timestamp =  DateTimeFormatter.ofPattern("HH_mm_ss", Locale.ENGLISH).withZone(ZoneId.of("GMT")).format(ZonedDateTime.now(ZoneOffset.UTC));
            String daystamp =  DateTimeFormatter.ofPattern("dd_MMM_yyyy", Locale.ENGLISH).withZone(ZoneId.of("GMT")).format(ZonedDateTime.now(ZoneOffset.UTC));
            String addr = client.getInetAddress().getHostAddress();
            in = client.getInputStream();

            IO.serverMessage("\n\nAssigned a new client " + addr + " to a separate thread\n");

            try {
                /*
                 * Read packet details.
                 */
                BufferedReader reader = new BufferedReader(new InputStreamReader(in));
                String message = reader.readLine();
                String name;
                int imageLength;

                /*
                 * Remove packet padding.
                 */
                message = message.replace("X",""); 
                String[] headers = message.split("#");

                try {
                    imageLength = validatePacket(headers);
                /**
                 * An issue with the image buffer means we can keep writing the readings.
                 * Set the image length to 0 for the later check and keep going.
                 */
                } catch (ImageBufferException err) {
                    IO.errOut("Error During Packet Validation", err);
                    imageLength = 0;
                /**
                 * A problem with the header packet means we must halt execution and throw
                 * an error. THe image is not work much without the associated readings.
                 */
                } catch (MalformedPacketException mal) {
                    throw mal;
                }

                /* 
                 * Get the device name.
                 */
                name = headers[1];

                /*
                 * Display packet details.
                 */
                io.displayPacket(addr, headers);

                
                /**
                 * Make sure folders exist for a given device.
                 */
                io.ensureFolderExists(String.format("images/%s/%s",name, daystamp));
                io.ensureFolderExists(String.format("readings/%s/%s",name, daystamp));

                /* 
                 * Write sensor data to csv file w/headers.
                 */
                String sensorDataFile = String.format("readings/%s/%s/%s.csv",name, daystamp, timestamp);
                io.writeReadings(headers, sensorDataFile, daystamp, timestamp);

                /* 
                 * Read image data from the socket and save it as a JPEG file.
                 * First check if imageLength is 0. If so, exit.
                 */
                if (imageLength == 0){return;}

                String imageName = String.format("images/%s/%s/%s.jpg",name, daystamp, timestamp);
                byte[] buffer = new byte[imageLength];
                buffer = in.readAllBytes();
                io.writeImage(imageLength, imageName, buffer);

            } catch (Exception err) {
                IO.errOut("Internal Server Error: ", err);
            }

        } catch (Exception err) {
            IO.errOut("Error reading client socket stream: ", err);
        } finally {
            try {
                client.close();
                IO.serverMessage("Connection closed");
            } catch (Exception err) {
                IO.errOut("Error closing socket: ", err);
            }
        }
    }


    public static void main(String[] args) {
        // new IO for io operations
        IO io = new IO();
        // set the default port for socket. 
        final int DEFAULTPORT = 880;
        int port = DEFAULTPORT;
        
        // Attempt to read custom port from args. if not specified correctly, use default.
        if (args.length != 1 ) {
            io.printUsage();
            port = DEFAULTPORT;
        }  else {
            port = io.stringToBoundedInt(args[0], 0, 65535, "port");
            if (port == -1) {
                port = DEFAULTPORT;
            }
        }

        // start server.
        Server server = new Server(io, port);
        server.start();
    }
}