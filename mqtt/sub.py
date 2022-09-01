import paho.mqtt.client as mqtt
import messaging
from os import getenv

# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe("carInfo/update")


# The callback function for received message
def on_message(client, userdata, msg):
    message = messaging.decodeMessage(msg.payload)
    print(f'{message["timestamp"]} {message["type"]}')
    if (msg.topic == "carInfo/update"):
        print(f'    position     {message["position"]}')
        print(f'    speed        {message["speed"]}')
        print(f'    acceleration {message["acceleration"]}')


mqtt_host_ip = getenv('clusterIP')
mqtt_host_port = int(getenv('mqttPort'))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_host_ip, mqtt_host_port, 60)
client.loop_forever()