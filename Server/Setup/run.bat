docker start fiware-orion
docker start mongo-db
::Espera a que se haya levantado el server para hacer el GET
timeout 5
::Timeout sin mostrarlo en consola
::timeout /T 5 > nul 

::Comprueba que todo haya salido bien
curl -X GET http://localhost:1026/version

cmd /k