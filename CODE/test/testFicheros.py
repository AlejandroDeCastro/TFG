from werkzeug.security import check_password_hash, generate_password_hash

contraseña=generate_password_hash('2')
print(contraseña)
