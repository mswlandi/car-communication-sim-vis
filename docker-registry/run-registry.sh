while read line; do export $line; done < ../.env

docker run -d \
  -p $REGISTRY_PORT:5000 \
  --restart=always \
  --name registry \
  -v $(pwd)/config.yml:/etc/docker/registry/config.yml \
  registry:2

# -v $REGISTRY_STORAGE:/var/lib/registry \