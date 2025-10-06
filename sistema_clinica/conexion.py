import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",       # Servidor
            user="root",            # Usuario de MySQL
            password="13921693LB",            # Tu contraseña (si tienes, escríbela aquí)
            database="clinica_villacarmen"  # Nombre de tu base de datos
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error de conexión a MySQL: {e}")
        return None
