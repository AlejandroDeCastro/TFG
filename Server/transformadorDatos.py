# coding=utf-8
import json

def convertir_json(input_file, output_file, mapeo_campos):
    with open(input_file, 'r') as archivo_entrada:
        datos = json.load(archivo_entrada)

    datos_nuevos = []
    for item in datos:
        nuevo_item = {}
        for campo_origen, campo_destino in mapeo_campos.items():
            if campo_origen in item:
                
                if campo_destino == 'id':
                    nuevo_item[campo_destino] = str(item[campo_origen])
                else:
                    nuevo_item[campo_destino] = item[campo_origen]

        
        #Nuevos campos NGSI que no están el JSON original
        nuevo_item['type'] = 'ParkingGroup'
        nuevo_item['category'] = {"type": "StructuredValue", "value": ["onStreet", "adjacentSpaces", "onlyDisabled"]
  }

        datos_nuevos.append(nuevo_item)

    with open(output_file, 'w') as archivo_salida:
        json.dump(datos_nuevos, archivo_salida, indent=2)


mapeo_campos = {'id_aparcamiento': 'id', 'plazastota': 'totalSpotNumber', 'plazaslibr': 'availableSpotNumber'}
convertir_json('Ficheros sin formatear\parkings_Valencia.json', 'Ficheros\parkings_Valencia.json', mapeo_campos)

