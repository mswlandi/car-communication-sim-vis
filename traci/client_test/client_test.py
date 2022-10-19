import socket

def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # choosing an arbitrary port for now
        # sock.bind(('0.0.0.0', 31415))
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


if __name__ == "__main__":
    client("127.0.0.1", 9999, "test 1\n")
    client("127.0.0.1", 9999, "test 2\n")
    client("127.0.0.1", 9999, "test 3\n")