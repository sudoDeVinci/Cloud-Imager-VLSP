package server_components;

/**
 * Class to handle IO, including FileIO
 */
public class IO {
        /**
         * Print a stylized usage message. 
        */
        public void printUsage() {
            System.err.println("Usage: java Server <port>");
        }


        /**
         * Validate string is an int with given bounds.
         * Alias given to number for printout.
         * @param num
         * @param lb
         * @param ub
         * @param alias
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
         * Print stylized server event message.
         * @param message
         */
        public void serverMessage(String message) {
            System.out.println(message);
        }


        /**
         * Print stylized errors to user.
         * @param err
         */
        public void errOut(String message, Exception err) {
            System.out.print(message);
            System.out.println(err.getMessage());
        }
}
