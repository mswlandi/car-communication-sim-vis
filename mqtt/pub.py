import paho.mqtt.client as mqtt
import time
import messaging
from os import getenv

def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')


mqtt_host_ip = getenv('clusterIP')
mqtt_host_port = int(getenv('mqttPort'))

client = mqtt.Client()
client.on_connect = on_connect
client.connect(mqtt_host_ip, mqtt_host_port, 60)

time.sleep(3)

carInfo = messaging.CarInfo((0,0), (100,0), (-2, 2))
message = messaging.Message("updateCarInfo", carInfo)
messageEncoded = messaging.encodeMessage(message)

for i in range(20):
    carInfo.speed = (carInfo.speed[0] + carInfo.acceleration[0], carInfo.speed[1] + carInfo.acceleration[1])
    carInfo.position = (carInfo.position[0] + carInfo.speed[0], carInfo.position[1] + carInfo.speed[1])
    message.updateData(carInfo)
    messageEncoded = messaging.encodeMessage(message)

    client.publish('carInfo/update', payload=messageEncoded, qos=1, retain=False)
    print(f'sent carInfo update to carInfo/update')
    time.sleep(1)

client.loop_forever()