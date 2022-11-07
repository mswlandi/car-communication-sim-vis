TraCI is the API to launch and control SUMO.
car_communication/ has a car communication docker image test
traci_main.py uses sockets_server_api.py to (on the future) launch car_communication pods and be a socket server to send information to the CCI pods.

if running the car_communication images on kind, you must run `kubectl apply -f kind_localhost_fix.yaml` so that the pods have access to the socket server on the same host