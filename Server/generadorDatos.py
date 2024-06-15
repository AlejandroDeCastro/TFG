# -*- coding: utf-8 -*-
import json
import os
import random
from datetime import datetime
import uuid
import threading
import time
import requests

# Guarda el PID en un archivo
with open('simulador.txt', 'w') as f:
    f.write(str(os.getpid()))

print("Simulador ejecutándose con PID:", os.getpid())

datos = {
    'Museo Evolución Humana': {'coordenadas': [42.338476, -3.697442], 'tipo' : 'Público', 'Interior/Exterior': 'Interior', 'Precio': '--€'},
    'Plaza Mayor': {'coordenadas':  [42.341148, -3.699824], 'tipo' : 'Privado', 'Interior/Exterior': 'Interior', 'Precio': '--€'},
    'Plaza Vega': {'coordenadas':  [42.335527, -3.711652], 'tipo' : 'Público' , 'Interior/Exterior': 'Interior', 'Precio': '--€'},
    'Plaza España': {'coordenadas':  [42.344406705937985, -3.6975360341261787], 'tipo' : 'Público' , 'Interior/Exterior': 'Interior', 'Precio': '--€'},
    'Virgen del Manzano': {'coordenadas':  [42.34632384614841, -3.6931517564298453], 'tipo' : 'Público', 'Interior/Exterior': 'Interior', 'Precio': '--€'},
    'Castillo de Burgos': {'coordenadas':  [42.34632384614841, -3.6931517564298453], 'tipo' : 'Público', 'Interior/Exterior': 'Exterior', 'Precio': 'GRATIS'}
}
parkingsBurgos = []

for nombre, caracteríticas in datos.items():
    parking = {}
    parking['nombre'] = nombre
    parking['coordenadas'] = caracteríticas['coordenadas']
    parking['tipo'] = caracteríticas['tipo']
    parking['Interior/Exterior'] = caracteríticas['Interior/Exterior']
    parking['Precio'] = caracteríticas['Precio']
    parkingsBurgos.append(parking)

def generadorDeDatosAleatorios():
    data_list = []
    for parking in parkingsBurgos:
        total_spot_number = random.randint(0, 1000)  # Genera un número aleatorio para totalSpotNumber entre 0 y 1000
        type_value = "ParkingGroup"  # Valor fijo para el campo "type"
        available_spot_number = random.randint(0, total_spot_number)  # Genera un número aleatorio para availableSpotNumber entre 0 y totalSpotNumber
        unique_id = str(uuid.uuid4())  # Genera un UUID único y lo convierte a cadena
        date_value = datetime.now().isoformat()  # Obtiene la fecha actual en formato ISO 8601

        data = {
            "type": type_value,
            "id": unique_id,
            "name": {
                "value": parking['nombre'],
                "type": "Text"    
            },
            "precio": {
                "value": parking['Precio'],
                "type": "Text"    
            },
            "Ubicacion": {
                "value": parking['Interior/Exterior'],
                "type": "Text"    
            },
            "availableSpotNumber": {
                "value": available_spot_number,
                "type": "Int",
                "metadata": {
                    "unit": {
                        "value": "Plazas",
                        "type": "Text"
                    }
                }
            },
            "totalSpotNumber": {
                "value": total_spot_number,
                "type": "Int",
                "metadata": {
                    "unit": {
                        "value": "Plazas",
                        "type": "Text"
                    }
                }
            },
            "tipo": {
                "value": parking['tipo'],
                "type": "Text"    
            },
            "location": {
                "type": "geo:json",
                "value": {
                    "type": "Point",
                    "coordinates": [parking['coordenadas'][1], parking['coordenadas'][0]]         
                }
            },
            "date": {
                "value": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "type": "DateTime"
            }
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

def update_data_list(data_list):
    while True:
        # Actualiza la fecha y plazas disponibles en cada diccionario de la lista
        for data in data_list:
            data['date']['value'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # Actualiza la fecha a la actual

            # Incrementa o decrementa aleatoriamente las plazas disponibles
            data['availableSpotNumber']['value'] += random.randint(-10, 10)

            # Asegura que las plazas disponibles no sean negativas ni excedan el total
            if data['availableSpotNumber']['value'] < 0:
                data['availableSpotNumber']['value'] = 0
            if data['availableSpotNumber']['value'] > data['totalSpotNumber']['value']:
                data['availableSpotNumber']['value'] = data['totalSpotNumber']['value']
        
        # Actualiza el JSON y las entidades en Orion
        nombreFichero = "Server/Ficheros/parkings_Burgos_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        save_json_to_file(data_list, nombreFichero)
        update_data_in_orion(data_list)

        # Espera 30 segundos antes de volver a actualizar los datos
        time.sleep(30)

def update_data_in_orion(data_list):
    context_broker_url = "http://localhost:1026"
    for data in data_list:
        id = data['id']
        url_actualizacion = f"{context_broker_url}/v2/entities/{id}/attrs"
        headers = {"Content-Type": "application/json"}
        datosActualizar = {
            "availableSpotNumber": {
                "value": data['availableSpotNumber']['value'],
                "type": "Int",
                "metadata": {
                    "unit": {
                        "value": "Plazas",
                        "type": "Text"
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
    try:
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(fichero), exist_ok=True)
        # Guarda los datos en el fichero
        with open(fichero, 'w') as f:
            json.dump(data_list, f, indent=4)
        print(f"Archivo JSON guardado en: {os.path.abspath(fichero)}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")

# Genera datos aleatorios y guarda en un archivo JSON
listaDeDatosAleatorios = generadorDeDatosAleatorios()
nombreFichero = "Server/Ficheros/parkings_Burgos_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
save_json_to_file(listaDeDatosAleatorios, nombreFichero)

# Inicia un hilo para actualizar periódicamente los datos en segundo plano
update_thread = threading.Thread(target=update_data_list, args=(listaDeDatosAleatorios,))
update_thread.daemon = True
update_thread.start()

# El programa principal sigue ejecutándose mientras el hilo de actualización se ejecuta en segundo plano
while True:
    time.sleep(1)  # Espera activa para mantener el programa principal en funcionamiento
