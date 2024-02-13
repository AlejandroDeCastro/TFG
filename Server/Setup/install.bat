docker pull mongo:4.2
docker pull fiware/orion:3.10.1
docker network create fiware_TFG
docker run -d --name=mongo-db --network=fiware_TFG --expose=27017 mongo:4.2 --bind_ip_all
docker run -d --name fiware-orion -h orion --network=fiware_TFG -p 1026:1026  fiware/orion:3.10.1 -dbhost mongo-db
cmd /k