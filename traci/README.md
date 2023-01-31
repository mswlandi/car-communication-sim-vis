TraCI is the API used to launch and control SUMO.
car_communication/ has the car communication docker image
traci_main.py uses sockets_server_api.py to launch car_communication pods and be a socket server to send information to the CCI pods.

Run `python3 traci_main.py` with the following optional arguments:

- `--step_length`: step interval of the SUMO simulation, in seconds
  - default: 0.05
- `--pod_limit`: Maximum number of car communication pods that are to be launched
  - default: 3
- `--vprefix`: The prefix that all car names share. if a car doesnt have it, throws an exception
  - default: veh
- `--sumo_binary`: The path to the sumo binary, including the actual binary name. default is just sumo, in that case you have to have installed sumo
  - default: sumo
- `--use_gui`: Use sumo-gui instead of sumo
- `--scenario_name`: The scenario type/name to run
  - default: normal
  - possible choices: normal, crash (supposes a carflow in the route file, and "carflow" as vprefix)
- `--scenario_path`: The path to the .sumofcg to run.
  - default: scenario_examples/normal/osm.sumocfg
- `--crash_time`: The desired time when the crash is supposed to happen. only used when scenario=crash.
  - default: 20

Example with the crash example scenario and a custom build of sumo:

`python3 traci_main.py --vprefix carflow --scenario_name crash --scenario_path "scenario_examples/crash/highwaycrash.sumocfg" --sumo_binary /home/marcos/Proj/sumo/bin/sumo --use_gui`


--scenario_path "/home/marcos/Proj/sumonetworks/stuttgart_vaihingen_universitat_dense/osm.sumocfg"