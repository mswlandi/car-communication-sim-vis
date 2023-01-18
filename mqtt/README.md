## MQTT

- add the emqx helm repository:
`helm repo add emqx https://repos.emqx.io/charts`
`helm repo update`

- install it:
`helm install emqx emqx/emqx --set service.type=NodePort`

- once it is installed, get the host port that was assigned to the pod's port 1883 (the TCP Port):
`export mqttPort=$(kubectl get svc | grep emqx | grep NodePort | grep -oP "1883:\K\d+(?=/TCP)")`
- to get the Websocket Port instead: (for the simulation dashboard for example)
`export mqttPort=$(kubectl get svc | grep emqx | grep NodePort | grep -oP ",8083:\K\d+(?=/TCP)")`
- also get node IP to access emqx externally
`export clusterIP=$(kubectl describe node | grep Addresses: -A 1 | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}")`

make sure to run the previous 2 commands before running pub.py and sub.py

to check emqx cluster status
`kubectl exec -it emqx-0 -- emqx_ctl cluster status`
change the number of pods in EMQX to 5 (it is recommended to be odd)
`helm upgrade --set replicaCount=5 emqx emqx/emqx`
to uninstall
`helm uninstall emqx`