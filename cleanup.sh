kind delete cluster
docker container stop kind-registry
docker container rm -v kind-registry
docker container stop minio
docker container rm -v minio