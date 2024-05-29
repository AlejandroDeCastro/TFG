import os
import time
import requests
from multiprocessing import Process

#Función que consulta las peticines de los usuarios en la base de datos y devuelve una lista de tuplas con las peticiones
def consultar_peticiones(db):

    cursor = db.database.cursor()

    cursor.execute("SELECT Ciudad, Característica, id_usuario, Formato, Periodicidad FROM registros")
    peticiones = cursor.fetchall()

    #Cierra la conexión con la base de datos
    cursor.close()
    

    return peticiones

# Función que consulta el fichero de las direcciones de los datos y devuelve un diccionario con todas las URL
def diccionarioURLs(db):

    cursor = db.database.cursor()
    datos = {}

    # Consulta SQL para obtener las ciudades, características y enlaces
    consulta_sql = "SELECT ciudad, característica, formato, enlace, periodicidad FROM datos"
    cursor.execute(consulta_sql)

    # Procesa los resultados
    for ciudad, caracteristica, formato, enlace, periodicidad in cursor:
        if ciudad not in datos:
            datos[ciudad] = {}
        if caracteristica not in datos[ciudad]:
            datos[ciudad][caracteristica] = {}
        datos[ciudad][caracteristica][formato] = [enlace,periodicidad]

    # Cierra el cursor
    cursor.close()

    return datos


def descargar_archivo(link, carpeta_destino, ciudad, característica, formato, periodicidad):


    while True:

        carpeta_ciudad = os.path.join(carpeta_destino, ciudad)

        #Verifica si la carpeta de la ciudad existe
        if not os.path.exists(carpeta_ciudad):
            os.makedirs(carpeta_ciudad)

        carpeta_caracteristica = os.path.join(carpeta_ciudad, característica)

        #Verifica si la carpeta de la característica existe
        if not os.path.exists(carpeta_caracteristica):
            os.makedirs(carpeta_caracteristica)

        carpeta_formato = os.path.join(carpeta_caracteristica, formato)

        #Verifica si la carpeta de la formato existe
        if not os.path.exists(carpeta_formato):
            os.makedirs(carpeta_formato)

        #Crea el nombre del archivo a partir de la característica
        nombre_archivo = f"{característica}_{ciudad}_{int(time.time())}.{formato}"
        ruta_destino = os.path.join(carpeta_formato, nombre_archivo)

        response = requests.get(link)
        if response.status_code == 200:
            with open(ruta_destino, 'wb') as f:
                f.write(response.content)
                print(f"Archivo guardado en: {ruta_destino}")
        else:
            print(f"Error al descargar el archivo de la URL: {link}")

        time.sleep(periodicidad)


#Función que inicia todos los demonios para las peticiones
def iniciar_demonios(db):
    
    #Diccionario de datos con la URL  
    datos = diccionarioURLs(db)

    #Consulta las peticiones de los usuarios desde la base de datos
    peticiones = consultar_peticiones(db)
    print(peticiones)

    carpeta_registros = "Registros"
    if not os.path.exists(carpeta_registros):
        os.makedirs(carpeta_registros)
    
    for peticion in peticiones:
        
        ciudad = peticion[0]
        característica = peticion[1]
        id_usuario = peticion[2]
        formato = peticion[3]
        periodicidad = peticion[4]

        link=datos[ciudad][característica][formato][0]

        #TEST PARA VALIDAR QUE ESTÁ LEYENDO LAS PETICIONES CORRECTAMENTE Y LAS ASOCIACIONES
        #print("El usuario "+str(id_usuario)+" quiere conocer la característica "+str(característica)+" de la ciudad de "+str(ciudad)+" cada "+str(periodicidad)+" segundos "+"y el link es "+str(link))

        usuario = "Usuario " + str(id_usuario)

        carpeta_usuario = os.path.join(carpeta_registros, usuario)

        if not os.path.exists(carpeta_usuario):
            os.makedirs(carpeta_usuario)


        proceso = Process(target=descargar_archivo, args=(link, carpeta_usuario, ciudad, característica, formato, periodicidad))
        proceso.start()

 


    #proceso.join()
        
