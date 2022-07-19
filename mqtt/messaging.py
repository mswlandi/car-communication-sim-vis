import jsonpickle
from datetime import datetime
from typing import List, Set, Dict, Tuple, Optional

class CarInfo():
    def __init__(self, position, speed, acceleration):
        self.position = position
        self.speed = speed
        self.acceleration = acceleration

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
    return jsonpickle.encode(message)

def decodeMessage(message):
    return jsonpickle.decode(message)