import os, sys
import time
import sockets_server_api
import env
import signal
import sys
import threading
import math
import argparse
from logger import get_logger
from car_communication import messaging

# make parent directory available to import k8sapi
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import k8sapi.api as k8sapi

# loads the traci lib path into the python load path so it can be imported
# https://github.com/wingsweihua/IntelliLight/blob/master/map_computor.py
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci

# ----- global variables (program states used in main and other functions) -----

# maps vehicle IDs to:
#   "id": str,
#   "LngLat": list[float],
#   "rotateX": float,
#   "rotateY": float,
#   "rotateZ": float,
# and has aditional control fields:
#   "wasUpdated": threading.Event   # had information updated, it's to be sent in the socket connection
#   "isToBeDeleted": threading.Event   # was deleted in the simulation, communication is supposed to end
cars_info = {}
stop_all_sockets_connections = threading.Event()
logger = get_logger(env.logger_name)

# ----- functions definition -----
def get_current_time():
    return traci.simulation.getCurrentTime() / 1000


def getMapOfVehicles():
    vehicle_id_list = traci.vehicle.getIDList()
    vehicle_list = []

    for vehicle_id in vehicle_id_list:
        x, y, altitude = traci.vehicle.getPosition3D(vehicle_id)
        lon, lat = traci.simulation.convertGeo(x, y)

        vehicle = {}
        vehicle["id"] = vehicle_id
        vehicle["position"] = [lon, lat]
        vehicle["altitude"] = altitude
        vehicle["speed"] = traci.vehicle.getSpeed(vehicle_id)
        vehicle["acceleration"] = traci.vehicle.getAcceleration(vehicle_id)
        vehicle["angle"] = traci.vehicle.getAngle(vehicle_id)
        vehicle["slope"] = traci.vehicle.getSlope(vehicle_id)
        vehicle_list.append(vehicle)
    
    return vehicle_list


def cleanup():
    '''Delete artifacts generated by the script (k8s namespace and pods) and close the traci and sockets APIs'''
    logger.info("cleaning up")
    k8sapi.delete_namespace_pods(env.k8sapi_namespace, prefix=env.car_pods_prefix)
    traci.close()
    stop_all_sockets_connections.set()
    sockets_server.stop()


def signal_handler(sig, frame):
    ''''SIGINT (CTRL-C) handler'''
    logger.info('\nYou pressed Ctrl+C!')

    cleanup()

    sys.exit(0)


# write to socket and receive response (can be ignored) on a loop
# when returns, socket connection is ended
def handle_CC_socket_connection(stream_request_handler, car_ID):
    global cars_info

    this_car_info = cars_info[car_ID]

    while True:
        if stop_all_sockets_connections.is_set():
            # leave it set for other handler threads
            stop_all_sockets_connections.set()
            break

        if this_car_info['isToBeDeleted'].is_set():
            logger.info(f"deleting car {car_ID}")
            del cars_info[car_ID]
            k8sapi.delete_pod(car_ID, env.k8sapi_namespace)
            break

        if this_car_info['wasUpdated'].is_set():
            this_car_info['wasUpdated'].clear()
            carData = messaging.exampleCarData
            carData['id'] = this_car_info['id']
            carData['LngLat'] = this_car_info['LngLat']
            carData["rotateX"] = this_car_info["rotateX"]
            carData["rotateY"] = this_car_info["rotateY"]
            carData["rotateZ"] = this_car_info["rotateZ"]

            messageEncoded = messaging.encodeMessage(carData, messaging.messageType.updateCarInfo)
            stream_request_handler.wfile.write(bytes(messageEncoded, "utf-8"))
            response = stream_request_handler.rfile.readline().strip().decode("utf-8")
            logger.debug(f"    {car_ID} wrote: {response}")
        
        time.sleep(0.001)
    
    return


# if id already exists in dict, doesn't update it
def create_or_update_car_info(vehicle):
    '''creates (if doesn't exist) or updates a car_info object based on the data of vehicle (returned by getMapOfVehicles)'''
    global cars_info

    car_info = {}

    if vehicle['id'] not in cars_info:
        car_info["wasUpdated"] = threading.Event()
        car_info["isToBeDeleted"] = threading.Event()
    else:
        car_info = cars_info[vehicle['id']]

    car_info["id"] = vehicle['id']
    car_info["LngLat"] = vehicle['position']
    car_info["rotateX"] = 0
    car_info["rotateY"] = math.pi * 2 - (float(vehicle['angle']) * math.pi / 180)
    car_info["rotateZ"] = 0
    car_info['wasUpdated'].set()

    cars_info[vehicle['id']] = car_info

    return car_info


# ----- main part -----
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--step_length", dest="step_length", help="step interval of the SUMO simulation, in seconds", default=0.05)
    parser.add_argument("--pod_limit", dest="pod_limit", help="Maximum number of car communication pods that are to be launched", default=3)
    parser.add_argument("--vprefix", dest="vehicleprefix", help="The prefix that all car names share. if a car doesnt have it, throws an exception", default="veh")
    parser.add_argument("--sumo_binary", dest="sumo_binary", help="The path to the sumo binary, including the actual binary name. default is just sumo, in that case you have to have installed sumo", default="sumo")
    parser.add_argument("--use_gui", dest="use_gui", help="Use sumo-gui instead of sumo", action='store_true')
    parser.add_argument("--scenario_name", dest="scenario_name", help="The scenario type/name to run. ('crash' supposes a carflow in the route file, and 'carflow' as vprefix)", default="normal", choices=['normal', 'crash', 'autobahn_crash'])
    parser.add_argument("--scenario_path", dest="scenario_path", help="The path to the .sumofcg to run.", default="scenario_examples/normal/osm.sumocfg")
    parser.add_argument("--crash_time", dest="crash_time", help="The desired time when the crash is supposed to happen. only used when scenario=crash.", default=40)
    args = parser.parse_args()
    
    env.car_pods_prefix = args.vehicleprefix
    step_length = args.step_length
    pod_limit = int(args.pod_limit)
    scenario_name = args.scenario_name
    crash_time = float(args.crash_time)

    sumoBinary = args.sumo_binary + "-gui" if args.use_gui else args.sumo_binary
    sumoCmd = [sumoBinary,
        "-c", args.scenario_path,
        "--precision.geo", "7",
        "--step-length", f"{step_length}",
        "--collision.mingap-factor", "0",
        "--collision.action", "warn",
        "--collision.stoptime", "50",
        "--step-method.ballistic", "false"]

    k8s_pod_image_name = "car_communication"
    k8s_pod_tag = "latest"

    coordinates_printed = False

    signal.signal(signal.SIGINT, signal_handler)

    # if using GUI, stays here until you press play on the GUI
    traci.start(sumoCmd)
    k8sapi.load_api()

    sockets_server = sockets_server_api.Server(env.host, env.port, handle_CC_socket_connection)
    sockets_server.start()

    time.sleep(5)

    if env.running_kind:
        created = k8sapi.create_namespace_if_inexistent(env.k8sapi_namespace)
        if created:
            # sketchy hack, remove if not using kind
            os.system(f"kubectl apply -f kind_localhost_fix.yaml --namespace={env.k8sapi_namespace}")

    for step in range(int(1600 / step_length)):
        traci.simulationStep()

        logger.debug(f"iteration {step}:")
        vehicle_list = getMapOfVehicles()
        for vehicle in vehicle_list:
            if not coordinates_printed:
                logger.info(f"first car inserted in coordinates {vehicle['position'][0]}, {vehicle['position'][1]}")
                coordinates_printed = True
            
            if vehicle['id'] not in cars_info:
                if not vehicle['id'].startswith(env.car_pods_prefix):
                    cleanup()
                    raise Exception(f"Car name ({vehicle['id']}) without the right prefix ({env.car_pods_prefix}) entered the simulation")
                
                if len(cars_info) < pod_limit:
                    # creates car info
                    new_car_info = create_or_update_car_info(vehicle)

                    k8sapi.create_pod(
                            new_car_info['id'],
                            k8s_pod_image_name,
                            k8s_pod_tag,
                            envs={
                                "SERVER_ADDRESS": "dockerhost",
                                "SERVER_PORT": "9999",
                                "CAR_ID": new_car_info['id'],
                                "PYTHONUNBUFFERED": "1"
                            },
                            namespace=env.k8sapi_namespace)
                    
                    logger.info(f"Created pod for car {new_car_info['id']}")
            
            else:
                # updates car info
                create_or_update_car_info(vehicle)
            
            # forced crash scenario
            if scenario_name == "crash":
                if vehicle['id'] == "carflow.2" and step * step_length > crash_time:
                    # set speed mode with a bitset that disregards maximum deceleration and safe speeds
                    traci.vehicle.setSpeedMode(vehicle['id'], 0b011010)
                    # makes the first car in the line brake suddenly as fast as possible
                    traci.vehicle.setSpeed(vehicle['id'], 0)
            
            if scenario_name == "autobahn_crash":
                if vehicle['id'].startswith("carflow-barrier") and step * step_length > crash_time:
                    # change to 3 cars
                    traci.vehicle.setSpeedMode(vehicle['id'], 0b011010)
                    traci.vehicle.setSpeed(vehicle['id'], 0)
            
        # goes through car_info objects that no longer exist in the simulation
        for car_id in set(cars_info) - set([vehicle['id'] for vehicle in vehicle_list]):
            cars_info[car_id]["isToBeDeleted"].set()

        time.sleep(step_length)
    
    # debugging sockets server
    # time.sleep(50)
    cleanup()