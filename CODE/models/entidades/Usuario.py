from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class Usuario(UserMixin):

    def __init__(self, id, usuario, contraseña, rol="usuario", nombreCompleto="") -> None:
        self.id = id
        self.usuario = usuario
        self.contraseña = contraseña
        self.rol=rol
        self.nombreCompleto = nombreCompleto
        

    # Función para comprobar si conincide la contraseña, con la coontraseña hasheada
    @classmethod #Con estse decorador puedo usar el método sin instanciar la clase
    def check_password(self, contraseñaHashed, contraseña):       
        return check_password_hash(contraseñaHashed, contraseña)

    # Función que devuelve la contraseña hasheada
    def hash_password(self):
        return generate_password_hash(self.contraseña)