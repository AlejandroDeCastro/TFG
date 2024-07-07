import mysql.connector

# Establece la conexión a la base de datos
database = mysql.connector.connect(
    #host="db",
    host="localhost",
    user='root',
    #password='root_password',
    password='',
    database='tfg'
)
