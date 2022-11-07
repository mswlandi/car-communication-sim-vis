cd car_communication
docker build -t car_communication .
docker tag car_communication localhost:5001/car_communication
docker push localhost:5001/car_communication