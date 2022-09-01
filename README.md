# Docker Image Catalog and Runner

## setup

- install [docker](https://docs.docker.com/get-docker/) [kind](https://kind.sigs.k8s.io/), [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) and [helm](https://helm.sh/docs/intro/install/)

- copy `.env.example` to a new file called `.env`. fill the variables accordingly.
- run `bash ./minio.sh` to run minio
- Access the minio console on `http://localhost:9001`. Input the username and password as on `.env`
  - create a service account, copy the access and secret keys to `docker-registry/config.yml`
  - create a bucket named `images`
- run `bash ./kind-registry.sh` to run the kubernetes cluster and docker registry

- run `cd webapp` and `bash ./run.sh` to run the webapp, which will be available on `http://localhost:5000/`

## monitoring

- add the prometheus and grafana helm repositories:
  `helm repo add grafana https://grafana.github.io/helm-charts`
  `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`

- install them by running:
  `helm install prometheus prometheus-community/prometheus --values monitoring/prometheus/values.yml`
  `helm install grafana grafana/grafana --values monitoring/grafana/values.yml`

- (optional) to see the prometheus webserver, run:
  ```bash
  export PROMETHEUS_POD_NAME=$(kubectl get pods --namespace default -l "app=prometheus,component=server" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace default port-forward $PROMETHEUS_POD_NAME 9090
  ```
  and visit `localhost:9090`

- access the grafana webserver by running `bash ./grafana-access.sh` and accessing the provided URL.
- import the dashboards from `monitoring/grafana/cluster.json` and `monitoring/grafana/pod.json`
- to save a dashboard after making changes, click on the share button, go to the export tab, turn on "Export for sharing externally", then "View JSON".

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

## clean up

`bash ./cleanup.sh`

## Architecture
### kubernetes cluster

The application is a kubernetes cluster that is ran on the desired machines (or simulated on a single one).
Currently the implementation (scripts) are made with [kind](https://kind.sigs.k8s.io/) in mind, but can easily be modified to allow for other tools.

### docker registry

The kubernetes cluster accesses a docker registry, as its personal and local image catalog. When one wants to make an image available for the system, it must be pushed to the docker registy, like so:

```bash
docker pull ubuntu # pulls the image from the docker hub. could be built locally.

docker tag ubuntu localhost:5001/my-ubuntu # tags the image to be used in the local registry
docker push localhost:5001/my-ubuntu # effectively makes the image available in the registry and so for the cluster

docker image rm ubuntu # you can remove the image from the local machine, both the original image 
docker image rm localhost:5001/my-ubuntu # and the tagged to be pushed to the registry
```

### webapp

provides a webapp for viewing the list of images in the registry, their tags and compressed sizes, as well as allowing one to execute an image into a specific node of the cluster.
The webapp uses the docker registry and kubernetes APIs to list and launch the images into the cluster's nodes.