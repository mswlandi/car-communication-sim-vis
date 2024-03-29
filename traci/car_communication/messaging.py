import jsonpickle
from datetime import datetime
from math import pi
from enum import Enum, auto


class messageType(Enum):
    updateCarInfo = auto() # send new car data
    closeConnection = auto() # last message before closing socket connection
    test = auto() # test the socket connection


exampleCarData = {
    "id": "first_car",
    "LngLat": [9.106607, 48.744746],
    "altitude": 0,
    "rotateX": 0,
    "rotateY": 5.5 * pi / 8,
    "rotateZ": 0
}


def encodeMessage(message, type=messageType.updateCarInfo):
    '''
    "type": messageType
    message contents:
        if "type" == messageType.updateCarInfo: send new car data
            "id": str, unique ID
            "LngLat": list[float], longitude and latitude
            "altitude": float, altitude in meters
            "rotateX": float, rotation in X axis (radians)
            "rotateY": float, rotation in Y axis (radians)
            "rotateZ": float, rotation in Z axis (radians)
        if "type" == messageType.closeConnection: last message before closing socket connection
            anything, contents are ignored
    '''
    msg = {}
    # if message is closeConnection, has to create a new dictionary to send
    if type == messageType.closeConnection:
        msg["type"] = type.value
        msg["timestamp"] = datetime.timestamp(datetime.now())
        msg["id"] = message
    # else, message is already a dictionary and use it as basis for message
    else:
        msg = message
        msg["type"] = type.value
        msg["timestamp"] = datetime.timestamp(datetime.now())
    
    return jsonpickle.encode(msg)

def decodeMessage(message):
    return jsonpickle.decode(message)