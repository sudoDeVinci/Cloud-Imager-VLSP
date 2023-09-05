package server_components.exceptions;

public class ImageBufferException extends Exception{
    private String message;

    public ImageBufferException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return String.format("ImageBufferException: %s",message);
    }
}
