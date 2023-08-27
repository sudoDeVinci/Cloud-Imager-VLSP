import java.util.Scanner;
/**
 * Class to handle IO, including FileIO
 */
public class IO {
        private Scanner scn;

        public IO(Scanner scn) {
            this.scn = scn;
        }

        public void printUsage() {
            System.err.println("Usage: java Server <port>");
        }
}
