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
            consulta="SELECT id, usuario, nombre_completo FROM usuarios WHERE id = {}".format(id)

            #Ejecución de la consulta
            cursor.execute(consulta)

            #Obtiene la fila resultante de la consulta
            row=cursor.fetchone()

            #Si hay se encuentra un usuario con ese nombre,  coge los datos y comprueba la contraseña
            if row != None:
                usuario=Usuario(row[0], row[1], None, row[2])
                cursor.close()
                return usuario
            else:
                cursor.close()
                return None

        except Exception as ex:
            raise Exception(ex)