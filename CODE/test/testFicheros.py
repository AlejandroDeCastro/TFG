import urllib.request
import requests
import xmltodict
import json

def xml_url_to_dict(url):

    """
    Esta función toma una URL que devuelve datos XML y los convierte en un diccionario.

    Args:
    url (str): URL que devuelve datos XML.

    Returns:
    dict: Diccionario que representa el contenido XML obtenido de la URL.
    """
    try:
        # Hacee una solicitud GET a la URL
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para respuestas no exitosas
        
        # Convierte el contenido XML a un diccionario
        xml_dict = xmltodict.parse(response.content)
        return xml_dict
    except requests.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
    except Exception as e:
        print(f"Error al convertir XML a diccionario: {e}")
    return None

#DATOS
enlaceAProbar="https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-publico"

# Uso de la función
diccionario = xml_url_to_dict(enlaceAProbar)

print(diccionario)
print(isinstance(diccionario, dict))