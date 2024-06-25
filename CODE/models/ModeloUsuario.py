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
    def register(self, db,usuario):

        try:
            # Crea el cursor
            cursor = db.cursor()

            # Insercción que se hace en la base de datos. 
            insercción="INSERT INTO usuarios (usuario, contraseña, nombre_completo, rol) VALUES (%s, %s, %s, %s)"
            data = (usuario.usuario, usuario.hash_password(), usuario.nombreCompleto, usuario.rol)

            # Ejecución de la insercción
            cursor.execute(insercción, data)
            db.commit()

            cursor.close()

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def existeUsuario(self, db, username):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # Consulta que se hace en la base de datos. 
            consulta="""SELECT id FROM usuarios WHERE usuario = '{}'""".format(username)
            
            # Ejecución de la consulta
            cursor.execute(consulta)

            # Obtiene la fila resultante de la consulta
            rows=cursor.fetchall()

            # Si hay resultados, hay alguien con ese nombre
            if rows == []:
                print("NO EXISTE")
                print(rows)
                cursor.close()
                return False
            else:
                print("EXISTE")
                print(rows)
                cursor.close()
                return True

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
            # Crea el cursor
            cursor = db.cursor()

            # Consulta que se hace en la base de datos. 
            consulta="SELECT id, usuario, rol, nombre_completo, favoritos FROM usuarios"

            # Ejecución de la consulta
            cursor.execute(consulta)

            # Obtiene las filas resultantes de la consulta
            rows=cursor.fetchall()
            usuarios={}

            # Si se encuentra un usuario con ese nombre,  coge los datos
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
    def get_registros_by_id(self, db, id_usuario):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # Consulta que se hace en la base de datos. 
            consulta="SELECT id, Ciudad, Característica, Formato, Periodicidad FROM registros WHERE id_usuario = {}".format(id_usuario)

            # Ejecución de la consulta
            cursor.execute(consulta)

            # Obtiene las filas resultantes de la consulta
            rows=cursor.fetchall()
            registros={}

            # Si encuentra registros para ese usuario los guarda en un diccionario
            if rows != None:
                # Itera sobre el array y añade los datos al diccionario
                for id, ciudad, caracteristica, formato, periodicidad in rows:
                    registros[id]=[ciudad, caracteristica, formato, periodicidad]
                    """
                    if ciudad not in registros:
                        registros[ciudad] = {}
                    if caracteristica not in registros[ciudad]:
                        registros[ciudad][caracteristica]={}
                    if formato not in registros[ciudad][caracteristica]:
                        registros[ciudad][caracteristica][formato] = []
                    registros[ciudad][caracteristica][formato].append(periodicidad)
                    """
                cursor.close()
                return registros
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)
    

    @classmethod
    def set_registro(self, db, id_usuario, ciudad, característica, formato, segundos):

        try:
            # Crea el cursor
            cursor = db.cursor()

            # Insercción que se hace en la base de datos. 
            insercción="INSERT INTO registros (id_usuario, Ciudad, Característica, Formato, Periodicidad) VALUES (%s, %s, %s, %s, %s)"
            data = (id_usuario, ciudad, característica, formato, segundos)

            # Ejecución de la insercción
            cursor.execute(insercción, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_registro(self, db, id):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # DELETE que se hace en la base de datos. 
            delete="DELETE FROM registros WHERE id = {}".format(id)

            # Ejecución de la insercción
            cursor.execute(delete)
            db.commit()

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_user(self, db, id):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # DELETE que se hace en la base de datos 
            delete="DELETE FROM usuarios WHERE id = {}".format(id)

            # Ejecución de la insercción
            cursor.execute(delete)
            db.commit()

        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def set_dato(self, db, id_usuario, ciudad, característica, formato, enlace, segundos):

        
        try:
            # Crea el cursor
            cursor = db.cursor()

            # Insercción que se hace en la base de datos. 
            insercción="INSERT INTO datos (ciudad, característica, formato, enlace, id_usuario, periodicidad) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (ciudad, característica, formato, enlace, id_usuario, segundos)

            # Ejecución de la insercción
            cursor.execute(insercción, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)
        

    @classmethod
    def delete_conjunto(self, db, ciudad, conjunto, formato):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # DELETE que se hace en la base de datos
            delete="DELETE FROM datos WHERE ciudad = %s AND característica = %s AND formato = %s"
            data = (ciudad, conjunto, formato)

            # Ejecución de la insercción
            cursor.execute(delete, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)


    @classmethod
    def set_traducción(self, db, original, traducción):

        
        try:
            # Crea el cursor
            cursor = db.cursor()

            # Insercción que se hace en la base de datos. 
            insercción="INSERT INTO traducciones (original, traducción) VALUES (%s, %s)"
            data = (original, traducción)

            # Ejecución de la insercción
            cursor.execute(insercción, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def delete_traducción(self, db, id):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # DELETE que se hace en la base de datos 
            delete="DELETE FROM traducciones WHERE id = {}".format(id)

            # Ejecución de la insercción
            cursor.execute(delete)
            db.commit()

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_traducciones(self, db):
        try:
            # Crea el cursor
            cursor = db.cursor()

            # Consulta que se hace en la base de datos. 
            consulta="SELECT id, original, traducción FROM traducciones"

            # Ejecución de la consulta
            cursor.execute(consulta)

            # Obtiene las filas resultantes de la consulta
            rows=cursor.fetchall()
            traducciones={}

            #Si hay traducciones se extraen en un diccionario
            if rows != None:
                for id, original, traducción in rows:
                    traducciones[id]={original : traducción}

                cursor.close()
                return traducciones
            else:
                cursor.close()
                return None

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
    def update_rol(self, db, id_usuario, rol):

        try:
            # Crea el cursor
            cursor = db.cursor()
            
            # Actualización que se hace en la base de datos. 
            actualización="UPDATE usuarios SET rol = %s WHERE id = %s"
            data = (rol, id_usuario)

            #Ejecución de la insercción
            cursor.execute(actualización, data)
            db.commit()

        except Exception as ex:
            raise Exception(ex)


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