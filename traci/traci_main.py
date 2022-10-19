import os, sys
import time
import sockets_server_api
import env

# loads the traci lib path into the python load path so it can be imported
# https://github.com/wingsweihua/IntelliLight/blob/master/map_computor.py
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci


# functions definition
def get_current_time():
    return traci.simulation.getCurrentTime() / 1000

def getMapOfVehicles():
    vehicle_id_list = traci.vehicle.getIDList()
    for vehicle_id in vehicle_id_list:
        vehicle_position = traci.vehicle.getPosition(vehicle_id)
        # print(f"    {vehicle_id}: {vehicle_position[0]}, {vehicle_position[0]}")


# main part
if __name__ == '__main__':
    sumoBinary = "/home/marcos/Proj/sumo/bin/sumo" #-gui
    sumoCmd = [sumoBinary, "-c", "/home/marcos/Proj/sumonetworks/quickstart/quickstart.sumocfg"]

    # if using GUI, stays here until you press play on the GUI
    traci.start(sumoCmd)

    sockets_server = sockets_server_api.Server(env.host, env.port)
    sockets_server.start()

    time.sleep(5)

    for step in range(20):
        traci.simulationStep()

        # print("iteration {step}:")
        getMapOfVehicles()

        time.sleep(0.1)
    
    traci.close()
    
    time.sleep(50)
    sockets_server.stop()