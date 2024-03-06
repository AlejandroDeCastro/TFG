import json
import random
from datetime import datetime

def generate_random_json():
    total_spot_number = random.randint(0, 1000)  # Genera un número aleatorio para totalSpotNumber entre 0 y 1000
    type_value = "ParkingGroup"  # Valor fijo para el campo "type"
    available_spot_number = random.randint(-1, total_spot_number)  # Genera un número aleatorio para availableSpotNumber entre -1 y totalSpotNumber
    id_value = "70.0"  # Valor fijo para el campo "id"
    date_value = datetime.now().isoformat()  # Obtiene la fecha actual en formato ISO 8601

    data = {
        "totalSpotNumber": total_spot_number,
        "type": type_value,
        "availableSpotNumber": available_spot_number,
        "id": id_value,
        "date": date_value
    }

    return data

def save_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        j
# Genera datos aleatorios y guarda en un archivo JSON
random_data = generate_random_json()
save_json_to_file(random_data, 'datosSensor.json')