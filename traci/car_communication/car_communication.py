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
                    if received_message != "":
                        decoded_message = messaging.decodeMessage(received_message)
                        if decoded_message["type"] == messaging.messageType.closeConnection:
                            print("received a close command. closing socket connection")
                            sock.close()
                            return
                        elif decoded_message["type"] == messaging.messageType.test:
                            send_message(sock, decoded_message["data"].upper())
                            print(f"Sent: {decoded_message['data'].upper()}")
                        elif decoded_message["type"] == messaging.messageType.updateCarInfo:
                            print(f"update for id: {decoded_message['id']}")
                            print(f"    LngLat: {decoded_message['LngLat']}")
                            print(f"    altitude: {decoded_message['altitude']}")
                            print(f"    rotateX: {decoded_message['rotateX']}")
                            print(f"    rotateY: {decoded_message['rotateY']}")
                            print(f"    rotateZ: {decoded_message['rotateZ']}")
                            send_message(sock, "received car data")
        
        except IOError as e:
            if e.errno == errno.EPIPE:
                print("error on the socket connection")
                sock.close()


if __name__ == "__main__":
    print("started CC Image")

    SRV = os.getenv('SERVER_ADDRESS')
    PORT = int(os.getenv('SERVER_PORT'))

    client(SRV, PORT)