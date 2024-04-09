from .entidades.Usuario import Usuario

class ModeloUsuario():

    @classmethod
    def login(self, db, user):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Consulta que se hace en la base de datos. Busca un usuario en concreto en la base de datos
            consulta="""SELECT id, usuario, contraseña, nombre_completo FROM usuarios 
            WHERE usuario = '{}'""".format(user.usuario) #CAMBIAR POR UN PROCEDIMIENTO ALMACENADO, QUIZÁ MÁS ADELANTE. ES MEJOR.

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene la fila resultante de la consulta
            row=cursor.fetchone()

            #Si hay se encuentra un usuario con ese nombre,  coge los datos y comprueba la contraseña
            if row != None:
                usuario=Usuario(row[0], row[1], Usuario.check_password(row[2], user.contraseña), row[3])
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
            consulta="SELECT id, usuario, nombre_completo, records FROM usuarios WHERE id = {}".format(id)

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene la fila resultante de la consulta
            row=cursor.fetchone()

            #Si hay se encuentra un usuario con ese nombre,  coge los datos y comprueba la contraseña
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
    def get_registros_by_id(self, db, id):
        try:
            #Crea el cursor
            cursor = db.cursor()

            #Consulta que se hace en la base de datos. 
            consulta="SELECT Ciudad, Característica FROM registros WHERE id_usuario = {}".format(id)

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene las filas resultantes de la consulta
            rows=cursor.fetchall()
            registros={}

            #Si hay se encuentra un usuario con ese nombre,  coge los datos y comprueba la contraseña
            if rows != None:
                # Itera sobre el array y añade los datos al diccionario
                for ciudad, caracteristica in rows:
                    if ciudad not in registros:
                        registros[ciudad] = []
                    registros[ciudad].append(caracteristica)

                print("VAMOS A VER QUE TAL")
                print(registros)
                cursor.close()
                return registros
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)