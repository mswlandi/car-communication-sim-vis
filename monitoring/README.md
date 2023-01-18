## monitoring

all of the commands are to be run from the root directory (parent of monitoring/)

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

- access the grafana webserver by running `bash monitoring/grafana-access.sh` and accessing the provided URL.
- import the dashboards from `monitoring/grafana/cluster.json` and `monitoring/grafana/pod.json`
- to save a dashboard after making changes, click on the share button, go to the export tab, turn on "Export for sharing externally", then "View JSON".