package server_components;

import server_components.IO;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.DatagramSocket;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Server {
    IO io;
    int port;

    public Server(IO io, int port) {
        this.io = io;
        this.port = port;
    }

    private String getLocalIP() {
        String ip = "";
        try(final DatagramSocket socket = new DatagramSocket()){
            socket.connect(InetAddress.getByName("8.8.8.8"), 10002);
            ip = socket.getLocalAddress().getHostAddress();
        } catch(Exception e) {
            io.errOut("Couldn't get local ip: ", e);
        }
        return ip;
    }


    /*
     * Main runtime loop for socket server.
     * Each connection is handed to the clientHandler() on a separate thread and submitted
     * to the  threadpool.
     */
    public void start() {
        ExecutorService threads = Executors.newFixedThreadPool(4);

        String ip = getLocalIP();
        
        try (ServerSocket serverSocket = new ServerSocket()) {
            serverSocket.bind(new InetSocketAddress(ip, port));
            System.out.println("Listening on: " + serverSocket.getInetAddress()+":"+serverSocket.getLocalPort());
            while (true){
                try {
                    Socket client = serverSocket.accept();
                    threads.submit(() -> {clientHandler(client);});
                } catch (Exception e){
                    io.errOut("Unable to Submit socket to threadpool: ", e);
			    }
            }
        } catch (IOException e) {
            io.errOut("Error starting server: ", e);
        } finally {
            threads.shutdown();
        }
    }

    /**
     * Handler for each connection, handled on a separate thread.
     * A socket is passed and analyzed.
     * @param client
     */
    private void clientHandler(Socket client) {
        InputStream in;
        OutputStream out;
        
        try {
            // Get client streams for bidirectional communication.
            in = client.getInputStream();
            out = client.getOutputStream();

            io.serverMessage("\nAssigned a new client to a separate thread\n");

            try {
                BufferedReader reader = new BufferedReader(new InputStreamReader(in));
                String message = reader.readLine();
                message = message.replace("X",""); 
                String[] headers = message.split("#",3);
                for (String i: headers) {
                    System.out.println(i);
                }
            } catch (Exception err) {
                io.errOut("Internal Server Error: ", err);
            }


        } catch (IOException err) {
            io.errOut("Error reading client socket stream: ", err);
        } finally {
            try {
                client.close();
            } catch (Exception err) {
                io.errOut("Error closing socket: ", err);
            }
        }
    }



    public static void main(String[] args) {
        // new io for io
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