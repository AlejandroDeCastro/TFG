from flask.helpers import redirect
from .entidades.Usuario import Usuario
import json

class ModeloUsuario():

    @classmethod
    def login(self, db, user):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Consulta que se hace en la base de datos. Busca un usuario en concreto en la base de datos
            consulta="""SELECT id, usuario, contraseña, rol, nombre_completo FROM usuarios 
            WHERE usuario = '{}'""".format(user.usuario) #CAMBIAR POR UN PROCEDIMIENTO ALMACENADO, QUIZÁ MÁS ADELANTE. ES MEJOR.

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene la fila resultante de la consulta
            row=cursor.fetchone()

            #Si hay se encuentra un usuario con ese nombre,  coge los datos y comprueba la contraseña
            if row != None:
                usuario=Usuario(row[0], row[1], Usuario.check_password(row[2], user.contraseña), row[3], row[4])
                cursor.close()
                return usuario
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Consulta que se hace en la base de datos. 
            consulta="SELECT id, usuario, rol, nombre_completo FROM usuarios WHERE id = {}".format(id)

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene la fila resultante de la consulta
            row=cursor.fetchone()

            #Si hay se encuentra un usuario con ese nombre,  coge los datos
            if row != None:
                usuario=Usuario(row[0], row[1], None, row[2], row[3])
                cursor.close()
                return usuario
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_users(self, db):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Consulta que se hace en la base de datos. 
            consulta="SELECT id, usuario, rol, nombre_completo, favoritos FROM usuarios"

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene las filas resultantes de la consulta
            rows=cursor.fetchall()
            usuarios={}

            #Si hay se encuentra un usuario con ese nombre,  coge los datos
            if rows != None:
                for id, usuario, rol, nombre_completo, favoritos in rows:
                    usuarios[id]=[usuario, rol, nombre_completo, favoritos]

                cursor.close()
                return usuarios
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_registros_by_id(self, db, id):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Consulta que se hace en la base de datos. 
            consulta="SELECT Ciudad, Característica, Formato, Periodicidad FROM registros WHERE id_usuario = {}".format(id)

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene las filas resultantes de la consulta
            rows=cursor.fetchall()
            registros={}

            #Si encuentra registros para ese usuario los guarda en un diccionario
            if rows != None:
                # Itera sobre el array y añade los datos al diccionario
                for ciudad, caracteristica, formato, periodicidad in rows:
                    if ciudad not in registros:
                        registros[ciudad] = {}
                    if caracteristica not in registros[ciudad]:
                        registros[ciudad][caracteristica]={}
                    if formato not in registros[ciudad][caracteristica]:
                        registros[ciudad][caracteristica][formato] = []
                    registros[ciudad][caracteristica][formato].append(periodicidad)

                cursor.close()
                return registros
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)
    

    @classmethod
    def set_registro(self, db, id_usuario, ciudad, característica, formato, periodicidad, unidad):

        if unidad != "segundos":
            segundos = str(conversionASegundos(periodicidad, unidad))
        else:
            segundos = periodicidad

        try:
            #Crea el cursor
            cursor = db.cursor()

            #Insercción que se hace en la base de datos. 
            insercción="INSERT INTO registros (id_usuario, Ciudad, Característica, Formato, Periodicidad) VALUES (%s, %s, %s, %s, %s)"
            data = (id_usuario, ciudad, característica, formato, segundos)

            #Ejecución de la insercción
            cursor.execute(insercción, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_registro(self, db, id_usuario, ciudad, característica, formato, periodicidad):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #DELETE que se hace en la base de datos. 
            delete="DELETE FROM registros WHERE id_usuario=%s AND Ciudad=%s AND Característica=%s AND Formato=%s AND Periodicidad=%s"
            data = (id_usuario, ciudad, característica, formato, periodicidad)

            #Ejecución de la insercción
            cursor.execute(delete, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)


    @classmethod
    def set_dato(self, db, id_usuario, ciudad, característica, formato, enlace, periodo, unidad):

        if periodo != 0 and unidad != None:
            if unidad != "segundos": # La opción de segundos no está disponible, pero quizá se incorpore en un futuro
                segundos = str(conversionASegundos(periodo, unidad))
            else:
                segundos = str(periodo)
        else:
            segundos="0"
        
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Insercción que se hace en la base de datos. 
            insercción="INSERT INTO datos (ciudad, característica, formato, enlace, id_usuario, periodicidad) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (ciudad, característica, formato, enlace, id_usuario, segundos)

            #Ejecución de la insercción
            cursor.execute(insercción, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex) 

    @classmethod
    def get_favoritos_by_id(self, db, id):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # Consulta para obtener los favoritos del usuario
            consulta = "SELECT favoritos FROM usuarios WHERE id = %s"
            cursor.execute(consulta, (id,))
            resultado = cursor.fetchone()
            
            if resultado:
                # La consulta devuelve una tupla, así que extraemos el valor de favoritos
                favoritos = resultado[0]
        
                return favoritos
            else:
                return ""  # El usuario no existe o no tiene favoritos

        except Exception as e:
            print(f"Error al obtener los favoritos: {e}")
            return None

    @classmethod
    def update_favoritos(self, db, id_usuario, favoritos):

        try:
            # Crea el cursor
            cursor = db.cursor()
            
            # Actualización que se hace en la base de datos. 
            actualización="UPDATE usuarios SET favoritos = %s WHERE id = %s"
            data = (favoritos, id_usuario)

            #Ejecución de la insercción
            cursor.execute(actualización, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)

def conversionASegundos(periodicidad, unidad):

    segundos=0
    periodicidad=int(periodicidad)

    if unidad == "meses":
        segundos = periodicidad * 31 * 24 * 3600
    elif unidad == "semanas":
        segundos = periodicidad * 7 * 24 * 3600
    elif unidad == "dias":
        segundos = periodicidad * 24 * 3600
    elif unidad == "horas":
        segundos = periodicidad * 3600
    elif unidad == "minutos":
        segundos = periodicidad * 60
    else:
        segundos=0 #Se ha pasado una unidad no registrada

    return segundos