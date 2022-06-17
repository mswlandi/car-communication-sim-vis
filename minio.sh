while read line; do export $line; done < ./.env

docker run                                      \
    -d                                          \
    -p 9000:9000                                \
    -p 9001:9001                                \
    --restart=always                            \
    --name minio                                \
    -v $(pwd)/docker-registry/storage:/storage  \
    -e "MINIO_ROOT_USER=${MINIO_USER}"          \
    -e "MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}"  \
    minio/minio                                 \
    server /storage --console-address ":9001"