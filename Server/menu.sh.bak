#!/bin/bash

function menu {
    clear
    echo "Menú:"
    echo "1. Iniciar servidor"
    echo "2. Parar servidor"
    echo "3. Mostrar entidades guardadas"
    echo "4. Borrar entidades guardadas"
    echo "5. Iniciar simulador"
    echo "6. Detener simulador"
    echo "7. Instalar servidor"
    echo "8. Desinstalar servidor"
    echo "9. Salir"
    read -p "Selecciona una opción (1-9): " option
    case $option in
        1) opcion_1 ;;
        2) opcion_2 ;;
        3) opcion_3 ;;
        4) opcion_4 ;;
        5) opcion_5 ;;
        6) opcion_6 ;;
        7) opcion_7 ;;
        8) opcion_8 ;;
        9) opcion_9 ;;
        *) echo "Opción inválida." ;;
    esac
}

function opcion_1 {
    docker start fiware-orion
    docker start mongo-db
    # Espera a que se haya levantado el server para hacer el GET
    sleep 5
    # Comprueba que todo haya salido bien
    curl -X GET http://localhost:1026/version
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_2 {
    docker stop fiware-orion
    docker stop mongo-db
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_3 {
    curl -G -X GET http://localhost:1026/v2/entities
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_4 {
    # Borra las entidades
    python3 limpiador.py
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_5 {
    # Ejecuta el script de Python en una nueva ventana
    python3 generadorDatos.py &
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_6 {
    # Lee el PID del archivo y mata el proceso
    if [ -f simulador.txt ]; then
        pid=$(<simulador.txt)
        kill $pid
        rm simulador.txt
    else
        echo "No se encontró el archivo simulador.txt."
    fi
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_7 {
    docker pull mongo:4.2
    docker pull fiware/orion:3.10.1
    docker network create fiware_TFG
    docker run -d --name=mongo-db --network=fiware_TFG --expose=27017 mongo:4.2 --bind_ip_all
    docker run -d --name fiware-orion -h orion --network=fiware_TFG -p 1026:1026 fiware/orion:3.10.1 -dbhost mongo-db
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_8 {
    docker rm -f fiware-orion
    docker rm -f mongo-db
    docker network rm fiware_TFG
    read -p "Presiona Enter para continuar..."
    menu
}

function opcion_9 {
    echo "Saliendo..."
    exit 0
}

menu