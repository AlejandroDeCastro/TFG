# -*- coding: utf-8 -*-
import json
import random
from datetime import datetime, timedelta
import uuid
import threading
import time
import requests

def generadorDeDatosAleatorios():
    data_list = []

    for _ in range(20):  # Genera 20 diccionarios de datos aleatorios
        total_spot_number = random.randint(0, 1000)  # Genera un número aleatorio para totalSpotNumber entre 0 y 1000
        type_value = "ParkingGroup"  # Valor fijo para el campo "type"
        available_spot_number = random.randint(-1, total_spot_number)  # Genera un número aleatorio para availableSpotNumber entre -1 y totalSpotNumber
        unique_id = str(uuid.uuid4())  # Genera un UUID único y lo convierte a cadena
        date_value = datetime.now().isoformat()  # Obtiene la fecha actual en formato ISO 8601

        data = {
            
            "type": type_value,
            "id": unique_id,
            "availableSpotNumber": {
                "value": available_spot_number,
                "type": "Int",
                "metadata": {
                    "unit": {
                    "value": "Plazas",
                    "type": "String"
                    }
                }
            },
            "totalSpotNumber": {
                "value": total_spot_number,
                "type": "Int",
                "metadata": {
                    "unit": {
                    "value": "Plazas",
                    "type": "String"
                    }
                }
            },        
            "date": {
                "value": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "type": "DateTime"
            }
            #"availableSpotNumber": available_spot_number,
            #"totalSpotNumber": total_spot_number,
            #"date": date_value
        }

        crear_registro(data)

        data_list.append(data)

    return data_list

def crear_registro(data):
    url = "http://localhost:1026/v2/entities"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = json.dumps(data)
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 201:
        print("Datos creados en Orion:", data)
    else:
        print("Error al crear datos en Orion:", response.text)
        print(response.status_code)

def update_data_list(data_list):
    
    while True:
        # Actualiza la fecha y plazas disponibles en cada diccionario de la lista
        for data in data_list:
            data['date']['value'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # Actualiza la fecha a la actual

            # Incrementa o decrementa aleatoriamente las plazas disponibles
            data['availableSpotNumber']['value'] += random.randint(-10, 10)

            # Asegura que las plazas disponibles no sean negativas
            if data['availableSpotNumber']['value'] < 0:
                data['availableSpotNumber']['value'] = 0
        
        #Actualiza el json
        nombreFichero="Ficheros/parkings_Valencia_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".json"
        save_json_to_file(data_list, nombreFichero)
        update_data_in_orion(data_list)

        # Espera 30 segundos antes de volver a actualizar los datos
        time.sleep(30)

# Función para actualizar los datos en el Context Broker
def update_data_in_orion(data_list):

    
    context_broker_url = "http://localhost:1026"

    for data in data_list:
        id = data['id']
        url_actualizacion = "{}/v2/entities/{}/attrs".format(context_broker_url, id)
        headers = {"Content-Type": "application/json"}
    
        print(id)
        print(url_actualizacion)

        datosActualizar = {
            "availableSpotNumber": {
                "value": data['availableSpotNumber']['value'],
                "type": "Int",
                "metadata": {
                        "unit": {
                            "value": "Plazas",
                            "type": "String"
                            }
                    }   
                },
                "date": {
                    "value": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "type": "DateTime"
                }
            }

    
        response = requests.patch(url_actualizacion, json=datosActualizar, headers=headers)

        if response.status_code == 204:
            print("Datos actualizados en Orion:", datosActualizar)
        else:
            print("Error al actualizar datos en Orion:", response.text)

def save_json_to_file(data_list, fichero):
    with open(fichero, 'w') as f:
        json.dump(data_list, f, indent=4)

# Genera datos aleatorios y guarda en un archivo JSON
listaDeDatosAleatorios = generadorDeDatosAleatorios()
nombreFichero="Ficheros/parkings_Valencia_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".json"
save_json_to_file(listaDeDatosAleatorios, nombreFichero)

# Inicia un hilo para actualizar periódicamente los datos en segundo plano
update_thread = threading.Thread(target=update_data_list, args=(listaDeDatosAleatorios,))
update_thread.daemon = True
update_thread.start()

# El programa principal sigue ejecutándose mientras el hilo de actualización se ejecuta en segundo plano
while True:
    time.sleep(1)  # Espera activa para mantener el programa principal en funcionamiento