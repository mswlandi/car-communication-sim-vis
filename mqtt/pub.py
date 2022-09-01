import paho.mqtt.client as mqtt
import time
import messaging
from os import getenv
from math import cos, asin, sin, atan2, degrees, radians

def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')


mqtt_host_ip = getenv('clusterIP')
mqtt_host_port = int(getenv('mqttPort'))

client = mqtt.Client()
client.on_connect = on_connect
client.connect(mqtt_host_ip, mqtt_host_port, 60)

time.sleep(3)

# origin and destination in [lng, lat], in degrees
def calcNewPosition(origin, destination, speed):
    earth_radius = 6378137 # in meters

    lon0 = radians(origin[0])
    lat0 = radians(origin[1])

    lon1 = radians(destination[0])
    lat1 = radians(destination[1])

    y = sin(lon1-lon0) * cos(lat1)
    x = cos(lat0)*sin(lat1) - sin(lat0)*cos(lat1)*cos(lon1-lon0)
    angle = atan2(y, x)

    lat = asin(sin(lat0)*cos(speed/earth_radius) + cos(lat0)*sin(speed/earth_radius)*cos(angle))
    lon = lon0 + atan2(sin(angle)*sin(speed/earth_radius)*cos(lat0), cos(speed/earth_radius)-sin(lat0)*sin(lat))

    return [degrees(lon), degrees(lat)]

# origin = [-73.987188, 40.734203] # new york
# destination = [66.945446, 39.810715] # uzbekistan
# speed = 200 * 1000
speed = 0.5
origin = [9.106639, 48.744466]
destination = [9.105249, 48.743953]

carInfo = messaging.exampleCarData
carInfo["LngLat"] = origin
messageEncoded = messaging.encodeMessage(carInfo)

print(f"{origin[1]},{origin[0]},red,marker,\"origin\"")
print(f"{destination[1]},{destination[0]},red,marker,\"destination\"")

for i in range(100):
    carInfo["LngLat"] = calcNewPosition(carInfo["LngLat"], destination, speed)
    messageEncoded = messaging.encodeMessage(carInfo)

    client.publish('carInfo/update', payload=messageEncoded, qos=1, retain=False)
    print(f'sent carInfo update to carInfo/update')

    print(f"{carInfo['LngLat'][0]},{carInfo['LngLat'][1]}")
    time.sleep(0.2)

client.loop_forever()