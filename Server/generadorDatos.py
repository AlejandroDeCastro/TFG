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
            "totalSpotNumber": total_spot_number,
            "type": type_value,
            "availableSpotNumber": available_spot_number,
            "id": unique_id,
            "date": date_value
        }

        data_list.append(data)

    return data_list

def update_data_list(data_list):
    
    while True:
        # Actualiza la fecha y plazas disponibles en cada diccionario de la lista
        for data in data_list:
            data['date'] = datetime.now().isoformat()  # Actualiza la fecha a la actual
            # Incrementa o decrementa aleatoriamente las plazas disponibles
            data['availableSpotNumber'] += random.randint(-10, 10)

            # Asegura que las plazas disponibles no sean negativas
            if data['availableSpotNumber'] < 0:
                data['availableSpotNumber'] = 0
        
        #Actualiza el json
        save_json_to_file(data_list, 'parkingsValenciaSimulado.json')
        update_data_in_orion(data_list)

        # Espera 5 segundos antes de volver a actualizar los datos
        time.sleep(30)

# Función para actualizar los datos en el Context Broker
def update_data_in_orion(data_list):
    url = "http://<ip_orion>:1026/v2/entities"  # Reemplazar <ip_orion> con la dirección IP de tu Orion Context Broker

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    for data in data_list:
        payload = json.dumps(data)
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            print("Datos actualizados en Orion:", data)
        else:
            print("Error al actualizar datos en Orion:", response.text)

def save_json_to_file(data_list, fichero):
    with open(fichero, 'w') as f:
        json.dump(data_list, f, indent=4)

# Genera datos aleatorios y guarda en un archivo JSON
listaDeDatosAleatorios = generadorDeDatosAleatorios()
save_json_to_file(listaDeDatosAleatorios, 'parkingsValenciaSimulado.json')

# Inicia un hilo para actualizar periódicamente los datos en segundo plano
update_thread = threading.Thread(target=update_data_list, args=(listaDeDatosAleatorios,))
update_thread.daemon = True
update_thread.start()

# El programa principal sigue ejecutándose mientras el hilo de actualización se ejecuta en segundo plano
while True:
    time.sleep(1)  # Espera activa para mantener el programa principal en funcionamiento