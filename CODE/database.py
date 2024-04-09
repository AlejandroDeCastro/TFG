import mysql.connector

# Establece la conexión a la base de datos
database = mysql.connector.connect(
    host="localhost",
    user='root',
    password='',
    database='tfg'
)
