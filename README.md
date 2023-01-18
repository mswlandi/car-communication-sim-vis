# Car Communication Simulation and Visualisation

Visualise a SUMO traffic simulation.
Made to be a car communication simulation, but currently only shows a normal SUMO simulation.

![demo](demo.gif)

## setup

### General
- install [docker](https://docs.docker.com/get-docker/) [kind](https://kind.sigs.k8s.io/), [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) and [helm](https://helm.sh/docs/intro/install/)

- copy `.env.example` to a new file called `.env`. fill the variables accordingly.
- run `bash ./minio.sh` to run minio
- Access the minio console on `http://localhost:9001`. Input the username and password as on `.env`
  - create a service account, copy the access and secret keys to `docker-registry/config.yml`
  - create a bucket named `images`
- run `bash ./kind-registry.sh` to run the kubernetes cluster and docker registry

### Image Catalog Webapp
The image catalog is a webapp that allows one to see the images currently in the local docker registry and launch them into the kubernetes cluster.
To setup and run the webapp, take a look at [image-catalog/webapp/README.md](image-catalog/webapp/README.md)

### Monitoring
it is possible to monitor the resource usage of the cluster using Prometheus and Grafana: take a look at [monitoring/README.md](monitoring/README.md).

### MQTT
As intermediary for the cars' communication, an MQTT broker and protocol are used.
To set it up, take a look at [mqtt/README.md](mqtt/README.md).

### Traci
The actual car traffic simulation is run by sumo, via the Traci API.
To run the simulation and flood the MQTT broker with car data, take a look at [traci/README.md](traci/README.md).

### Simulation Dashboard
To see the cars in an interactive 3d map, you can install an run a react app for visualisation: take a look at [simulation-dashboard/README.md](simulation-dashboard/README.md)

## clean up

`bash ./cleanup.sh`