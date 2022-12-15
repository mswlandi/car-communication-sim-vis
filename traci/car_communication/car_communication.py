import os
import socket
import select
import sys
import errno
import messaging
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f'Connected to MQTT server with result code {rc}')


mqtt_host_ip = "emqx.default.svc.cluster.local"
mqtt_host_port = 1883

client = mqtt.Client()
client.on_connect = on_connect
client.connect(mqtt_host_ip, mqtt_host_port, 60)

def send_message(sock, message):
    '''sends message in bytes and with a trailing new line'''
    sock.sendall(bytes(f"{message}\n", 'utf-8'))


def CarCommunication(ip, port):
    global client

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.setblocking(0)

        try:
            # identifies itself
            car_id = os.getenv('CAR_ID')
            send_message(sock, car_id)
            print(f"sent: {car_id}")

            # awaits for data and responds
            while True:
                ready = select.select([sock], [], [])
                if ready[0]:
                    received_message = str(sock.recv(4096), 'utf-8')
                    if received_message != "":
                        # deal with the sockets message and then send MQTT message accordingly
                        decoded_message = messaging.decodeMessage(received_message)
                        if decoded_message["type"] == messaging.messageType.closeConnection.value:
                            print("received a close command. closing socket connection")
                            sock.close()
                            # client.publish('carInfo/close', payload=car_id, qos=1, retain=False)
                            return
                        elif decoded_message["type"] == messaging.messageType.test.value:
                            send_message(sock, decoded_message["data"].upper())
                            print(f"Sent: {decoded_message['data'].upper()}")
                        elif decoded_message["type"] == messaging.messageType.updateCarInfo.value:
                            print(f"update for id: {decoded_message['id']}")
                            print(f"    LngLat: {decoded_message['LngLat']}")
                            print(f"    altitude: {decoded_message['altitude']}")
                            print(f"    rotateX: {decoded_message['rotateX']}")
                            print(f"    rotateY: {decoded_message['rotateY']}")
                            print(f"    rotateZ: {decoded_message['rotateZ']}")
                            send_message(sock, "ack")

                            # assemble MQTT message from sockets data
                            carInfo = messaging.exampleCarData
                            carInfo['id'] = decoded_message['id']
                            carInfo['LngLat'] = decoded_message['LngLat']
                            carInfo['altitude'] = decoded_message['altitude']
                            carInfo['rotateX'] = decoded_message['rotateX']
                            carInfo['rotateY'] = decoded_message['rotateY']
                            carInfo['rotateZ'] = decoded_message['rotateZ']
                            messageEncoded = messaging.encodeMessage(carInfo)
                            client.publish('carInfo/update', payload=messageEncoded, qos=1, retain=False)
        
        except IOError as e:
            if e.errno == errno.EPIPE:
                print("error on the socket connection")
                sock.close()


if __name__ == "__main__":
    print("started CC Image")

    SRV = os.getenv('SERVER_ADDRESS')
    PORT = int(os.getenv('SERVER_PORT'))

    CarCommunication(SRV, PORT)