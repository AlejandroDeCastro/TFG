import os
import time
import requests
from multiprocessing import Process

#Función que consulta las peticines de los usuarios en la base de datos y devuelve una lista de tuplas con las peticiones
def consultar_peticiones(db):

    cursor = db.database.cursor()

    cursor.execute("SELECT Ciudad, Característica, id_usuario, Periodicidad FROM registros")
    peticiones = cursor.fetchall()

    #Cierra la conexión con la base de datos
    cursor.close()
    

    return peticiones

#Función que consulta el fichero de las direcciones de los datos y devuelve un diccionario con todas las URL
def diccionarioURLs(nombre_archivo):

    datos = {}

    with open(nombre_archivo, 'r') as archivo:

        for linea in archivo:
            #Divide la línea en partes separadas por el guion -
            ciudad, caracteristica, url = linea.strip().split(' - ')
            #Verifica si la ciudad ya está en el diccionario
            if ciudad not in datos:
                datos[ciudad] = {}
            #Añade la característica y URL al diccionario de la ciudad correspondiente
            datos[ciudad][caracteristica] = url

    return datos


def descargar_archivo(link, carpeta_destino, ciudad, característica, periodicidad):


    while True:

        nombre_archivo = f"{característica}{int(time.time())}.json"
        ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
        response = requests.get(link)
        if response.status_code == 200:
            with open(ruta_destino, 'wb') as f:
                f.write(response.content)
                print(f"Archivo guardado en: {ruta_destino}")
        else:
            print(f"Error al descargar el archivo de la URL: {link}")

        time.sleep(periodicidad)


#Función que inicia todos los demonios para las peticiones
def iniciar_demonios(db, nombre_archivo):

    #Ejemplo de uso:
    #nombre_archivo = r"C:\Users\alexd\Desktop\TFG\PROGRAM\CODE\Datos\datos.txt"
    datos = diccionarioURLs(nombre_archivo)

    #Consulta las peticiones de los usuarios desde la base de datos
    peticiones = consultar_peticiones(db)
    print(peticiones)

    for peticion in peticiones:
        
        ciudad = peticion[0]
        característica = peticion[1]
        id_usuario = peticion[2]
        periodicidad = peticion[3]

        link=datos[ciudad][característica]

        #TEST PARA VALIDAR QUE ESTÁ LEYENDO LAS PETICIONES CORRECTAMENTE Y LAS ASOCIACIONES
        #print("El usuario "+str(id_usuario)+" quiere conocer la característica "+str(característica)+" de la ciudad de "+str(ciudad)+" cada "+str(periodicidad)+" segundos "+"y el link es "+str(link))

        
        carpeta_usuario = str(id_usuario)
        if not os.path.exists(carpeta_usuario):
            os.makedirs(carpeta_usuario)


        proceso = Process(target=descargar_archivo, args=(link, carpeta_usuario, ciudad, característica, periodicidad))
        proceso.start()


    #proceso.join()
        
