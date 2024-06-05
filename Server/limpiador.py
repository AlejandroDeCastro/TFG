import requests

# Configuración del Orion Context Broker
orion_url = "http://localhost:1026/v2/entities"  
headers = {
    "Accept": "application/json"
}

# Obtener todas las entidades
response = requests.get(orion_url, headers=headers)

if response.status_code == 200:
    entities = response.json()
    
    # Eliminar cada entidad
    for entity in entities:
        entity_id = entity['id']
        delete_url = f"{orion_url}/{entity_id}"
        
        delete_response = requests.delete(delete_url, headers=headers)
        
        if delete_response.status_code == 204:
            print(f"Entidad {entity_id} eliminada correctamente.")
        else:
            print(f"Error al eliminar la entidad {entity_id}: {delete_response.status_code} - {delete_response.text}")
else:
    print(f"Error al obtener las entidades: {response.status_code} - {response.text}")
