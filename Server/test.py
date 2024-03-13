# -*- coding: utf-8 -*-
import json
import requests

data = {
    "type": "ParkingGroup",
    "id": "111"
}

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