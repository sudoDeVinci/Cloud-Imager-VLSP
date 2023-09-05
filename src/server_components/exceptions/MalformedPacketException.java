package server_components.exceptions;

public class MalformedPacketException extends Exception{
    private String message;

    public MalformedPacketException(String message) {
        super(message);
    }

    @Override 
    public String getMessage() {
        return String.format("MalformedPacketException: %s",message);
    }
}
