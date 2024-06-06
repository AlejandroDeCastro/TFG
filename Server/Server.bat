@echo off
:menu
cls
echo Menú:
echo 1. Iniciar servidor
echo 2. Parar servidor
echo 3. Mostrar entidades guardadas
echo 4. Borrar entidades guardadas
echo 5. Iniciar simulador
echo 6. Detener simulador
echo 7. Instalar servidor
echo 8. Desinstalar servidor
echo 9. Salir
set /p option=Selecciona una opción (1-9):

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
:: Borra las entidades
start python limpiador.py
pause
goto menu

:opcion_5
:: Ejecuta el script de Python en una nueva ventana
start python generadorDatos.py
pause
goto menu

:opcion_6
:: Lee el PID del archivo y mata el proceso
if exist simulador.txt (
    set /p pid=<simulador.txt
    taskkill /PID %pid% /F
    del simulador.txt
) else (
    echo No se encontró el archivo simulador.txt.
)
pause
goto menu

:opcion_7
docker pull mongo:4.2
docker pull fiware/orion:3.10.1
docker network create fiware_TFG
docker run -d --name=mongo-db --network=fiware_TFG --expose=27017 mongo:4.2 --bind_ip_all
docker run -d --name fiware-orion -h orion --network=fiware_TFG -p 1026:1026  fiware/orion:3.10.1 -dbhost mongo-db
pause
goto menu

:opcion_8
docker rm fiware-orion
docker rm mongo-db
docker network rm fiware_TFG
pause
goto menu

:opcion_9
echo Saliendo...
exit /b
