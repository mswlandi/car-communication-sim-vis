TraCI is the API to launch and control SUMO.
client_test/ has a car communication docker image test
traci_main.py uses sockets_server_api.py to (on the future) launch client_test pods and be a socket server to send information to the CCI pods.