import threading
import socketserver
import time
from logger import get_logger
import env
from car_communication import messaging


logger = get_logger(env.logger_name)

class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        logger.debug(f"{self.client_address[0]} wrote:")
        logger.debug(self.data.decode("utf-8"))

        this_car_ID = self.data.decode("utf-8")

        # handle connection. self is passed as first argument
        self.socket_connection_handler(this_car_ID)
        
        messageEncoded = messaging.encodeMessage({"data": "close connection"}, messaging.messageType.closeConnection)
        self.wfile.write(bytes(messageEncoded, "utf-8"))
        logger.debug(f"closed connection with {this_car_ID}")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# holds the server and the server thread objects
class Server():
    # returns the server thread
    def __init__(self, host, port, socket_connection_handler):
        self.ip = host

        # override socket connection on address if it is busy
        ThreadedTCPServer.allow_reuse_address = True

        # assign handler function
        ThreadedTCPRequestHandler.socket_connection_handler = socket_connection_handler

        self.server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

        # get port from here in the case that server is initialized with port 0 (arbitrary port)
        ip, self.port = self.server.server_address

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True


    # starts the server thread
    def start(self):
        logger.info("sockets server starting")
        self.server_thread.start()


    # stops the server (thread closes automatically)
    def stop(self):
        logger.info("sockets server stopping")
        self.server.shutdown()
        self.server.server_close()


# manual example without using the class Server
if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    logger.info("Server loop running in thread:", server_thread.name)

    server.shutdown()
    server.server_close()