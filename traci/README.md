TraCI is the API used to launch and control SUMO.
car_communication/ has the car communication docker image
traci_main.py uses sockets_server_api.py to launch car_communication pods and be a socket server to send information to the CCI pods.

to run, with sumo installed, in `traci_main.py`, adjust the variables `sumoBinary`, `sumoCmd` and `pod_limit`, then run `python3 traci_main.py`.