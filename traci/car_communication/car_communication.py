import os
import socket
import select
import sys
import errno
import messaging

def send_message(sock, message):
    '''sends message in bytes and with a trailing new line'''
    sock.sendall(bytes(f"{message}\n", 'utf-8'))


def client(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.setblocking(0)

        try:
            # identifies itself
            pod_name = os.getenv('POD_NAME')
            send_message(sock, pod_name)
            print(f"sent: {pod_name}")

            # awaits for data and responds
            while True:
                ready = select.select([sock], [], [])
                if ready[0]:
                    received_message = str(sock.recv(4096), 'utf-8')
                    print(f"Received: {received_message}")
                    send_message(sock, received_message.upper())
                    print(f"Sent: {received_message.upper()}")
        
        except IOError as e:
            if e.errno == errno.EPIPE:
                print("error on the socket connection")
                sock.close()


if __name__ == "__main__":
    SRV = os.getenv('SERVER_ADDRESS')
    PORT = int(os.getenv('SERVER_PORT'))

    client(SRV, PORT)