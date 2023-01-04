import paho.mqtt.client as mqtt
import messaging
from os import getenv

# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe("carInfo/+/update")
    client.subscribe("carInfo/+/close")


# The callback function for received message
def on_message(client, userdata, msg):
    message = messaging.decodeMessage(msg.payload)
    print(f'{message["timestamp"]} {messaging.messageType(message["type"])}')
    if (msg.topic.endswith("/update")):
        print(f'    ID     {message["id"]}')
        print(f'    LngLat     {message["LngLat"]}')
    if (msg.topic.endswith("/close")):
        print(f'    ID     {message["id"]}')


mqtt_host_ip = getenv('clusterIP')
mqtt_host_port = int(getenv('mqttPort'))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_host_ip, mqtt_host_port, 60)
client.loop_forever()