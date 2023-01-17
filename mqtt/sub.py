import paho.mqtt.client as mqtt
import messaging
import os
import time
import signal

# Global Variables
car_data_list = {}
historic_car_data_list = {}
should_stop_loop = False


def signal_handler(sig, frame):
    ''''SIGINT (CTRL-C) handler'''
    global should_stop_loop
    print("\nctrl-c pressed, stopping...")
    should_stop_loop = True


# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe("carInfo/+/update")
    client.subscribe("carInfo/+/close")


# The old callback function for received message - very simple, use with client.loop_forever()
def on_message_old(client, userdata, msg):
    message = messaging.decodeMessage(msg.payload)
    print(f'{message["timestamp"]} {messaging.messageType(message["type"])}')
    if (msg.topic.endswith("/update")):
        print(f'    ID     {message["id"]}')
        print(f'    LngLat     {message["LngLat"]}')
    if (msg.topic.endswith("/close")):
        print(f'    ID     {message["id"]}')


# The callback function for received message
def on_message(client, userdata, msg):
    global any_update
    message = messaging.decodeMessage(msg.payload)
    if (msg.topic.endswith("/update")):
        if message["id"] not in car_data_list:
            car_data_list[message["id"]] = {
                "data": message["LngLat"],
                "last_updated": time.time(),
                "record": 0
            }
        else:
            car_data_list[message["id"]]["data"] = message["LngLat"]
            car_data_list[message["id"]]["last_updated"] = time.time()
    if (msg.topic.endswith("/close")):
        deleted_car = car_data_list.pop(message["id"], None)
        historic_car_data_list[message["id"]] = deleted_car

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    mqtt_host_ip = os.getenv('clusterIP')
    mqtt_host_port = int(os.getenv('mqttPort'))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_host_ip, mqtt_host_port, 60)
    client.loop_start()

    while not should_stop_loop:
        os.system("clear")
        for id in car_data_list:
            time_since_last = time.time() - car_data_list[id]['last_updated']
            if time_since_last > car_data_list[id]['record']:
                car_data_list[id]['record'] = time_since_last
            print(f"{id}: {time_since_last : <26} record: {car_data_list[id]['record']}")
        
        print("\nhistoric (deleted cars):")
        for id in historic_car_data_list:
            print(f"{id}: {historic_car_data_list[id]['record']}")
        time.sleep(0.03)

    client.loop_stop()