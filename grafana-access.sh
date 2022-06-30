GRAFANA_PASSWORD=$(kubectl get secret --namespace default grafana -o jsonpath="{.data.admin-password}" | base64 --decode)
GRAFANA_NODE_PORT=$(kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}" services grafana)
GRAFANA_NODE_IP=$(kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}")
echo Grafana URL: http://$GRAFANA_NODE_IP:$GRAFANA_NODE_PORT
echo User: admin
echo Password: $GRAFANA_PASSWORD