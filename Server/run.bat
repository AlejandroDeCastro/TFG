docker pull mongo:4.2
docker pull fiware/orion
docker network create fiware_TFG
docker run -d --name=mongo-db --network=fiware_TFG --expose=27017 mongo:4.2 --bind_ip_all
docker run -d --name fiware-orion -h orion --network=fiware_TFG -p 1026:1026  fiware/orion -dbhost mongo-db

::Espera a que se haya levantado el server para hacer el GET
timeout 5
::Timeout sin mostrarlo en consola
::timeout /T 5 > nul 

::Comprueba que todo haya salido bien
curl -X GET http://localhost:1026/version

cmd /k