import jsonpickle
from datetime import datetime
from math import pi

class CarInfo():
    def __init__(self, position, speed, acceleration):
        self.position = position
        self.speed = speed
        self.acceleration = acceleration

exampleCarData = {
    "id": "first_car",
    "LngLat": [9.106607, 48.744746],
    "altitude": 0,
    "rotateX": 0,
    "rotateY": 5.5 * pi / 8,
    "rotateZ": 0
}

class Message():
    def __init__(self, type, data):
        '''
        Parameters:
            type: "updateCarInfo"
            data: CarInfo object if type == "updateCarInfo"
        '''
        self.timestamp = datetime.timestamp(datetime.now())
        self.type = type
        self.data = data
    
    def updateData(self, data):
        '''
        Updates data and the timestamp
        '''
        self.data = data
        self.timestamp = datetime.timestamp(datetime.now())

def encodeMessage(message):
    message["type"] = "updateCarInfo"
    message["timestamp"] = datetime.timestamp(datetime.now())
    return jsonpickle.encode(message)

def decodeMessage(message):
    return jsonpickle.decode(message)