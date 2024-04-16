from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class Usuario(UserMixin):

    def __init__(self, id, usuario, contraseña, nombreCompleto="") -> None:
        self.id = id
        self.usuario = usuario
        self.contraseña = contraseña
        self.nombreCompleto = nombreCompleto

    #Método para comprobar si conincide la contraseña, con la coontraseña hasheada
    @classmethod #Con estse decorador puedo usar el método sin instanciar la clase
    def check_password(self, contraseñaHashed, contraseña):       
        return check_password_hash(contraseñaHashed, contraseña)

#print(generate_password_hash('1'))