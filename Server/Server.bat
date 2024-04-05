@echo off
:menu
cls
echo Menú:
echo 1. Iniciar
echo 2. Parar
echo 3. Comprobar entidades
echo 4. Transformar y cargar datos
echo 5. Instalar
echo 6. Desinstalar
echo 7. Salir
set /p option=Selecciona una opción (1-7):

goto opcion_%option%

:opcion_1
docker start fiware-orion
docker start mongo-db
::Espera a que se haya levantado el server para hacer el GET
timeout 5
::Timeout sin mostrarlo en consola
::timeout /T 5 > nul 

::Comprueba que todo haya salido bien
curl -X GET http://localhost:1026/version
pause
goto menu

:opcion_2
docker stop fiware-orion
docker stop mongo-db
pause
goto menu

:opcion_3
curl -G -X GET http://localhost:1026/v2/entities
pause
goto menu

:opcion_4
call Setup/POST.bat
goto menu

:opcion_5
docker pull mongo:4.2
docker pull fiware/orion:3.10.1
docker network create fiware_TFG
docker run -d --name=mongo-db --network=fiware_TFG --expose=27017 mongo:4.2 --bind_ip_all
docker run -d --name fiware-orion -h orion --network=fiware_TFG -p 1026:1026  fiware/orion:3.10.1 -dbhost mongo-db
pause
goto menu

:opcion_6
docker rm fiware-orion
docker rm mongo-db
docker network rm fiware_TFG
pause
goto menu

:opcion_7
echo Saliendo...
exit /b