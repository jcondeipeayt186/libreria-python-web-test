from decouple import config
from mysql.connector import pooling

import mysql.connector

# Variable global
USO_POOL_DE_CONEXIONES = True

# Conexión a MySQL
# Configuración para conectarse a la base de datos MySQL.
# El diccionario `db_config` almacena los parámetros necesarios para la conexión.
db_config = {
    'host': config('DB_HOST'),
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
    'database': config('DB_NAME')
}

# Conexión a la base de datos utilizando la configuración anterior.
# El doble asterisco (`**`) descompone el diccionario `db_config` en argumentos clave-valor.
# Es equivalente a escribir: mysql.connector.connect(host='localhost', user='root', password='password', database='libreria').
#Esto simplifica el código cuando hay muchos argumentos.
if(USO_POOL_DE_CONEXIONES):
    # Crear un pool de conexiones
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="mi_pool",
            pool_size=5,  # Número máximo de conexiones en el pool
            **db_config
        )
        print("Pool de conexiones creado exitosamente.")
    except mysql.connector.Error as e:
        print(f"Error al crear el pool de conexiones: {e}")    
else: 
    try:
        conn = mysql.connector.connect(**db_config)
    except mysql.connector.Error as e:
        print(f"Error al crear la conexión: {e}")  






def abrir_conexion():
    """
    Abre una conexión a la base de datos y retorna la conexión y el cursor.
    """
    if(USO_POOL_DE_CONEXIONES):
        conn = __obtener_conexion_pool()        
    else:    
        conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    return conn, cursor


# Función para obtener una conexión del pool
def __obtener_conexion_pool():
    """
    Obtiene una conexión del pool.
    """
    try:
        return pool.get_connection()
    except mysql.connector.Error as e:
        print(f"Error al obtener la conexión del pool: {e}")
        return None

# Función para cerrar la conexión
def cerrar_conexion(conn, cursor=None):
    """
    Cierra el cursor y devuelve la conexión al pool o cierra conexion.
    """
    if cursor:
        cursor.close()
    if conn:
        conn.close()  # Si usa Pool, Devuelve la conexión al pool sino cierra la conexion directamente


""" 
#Ejemplo de uso:

def obtener_libros():
    
    #Ejemplo de función que realiza una consulta a la base de datos.
    
    conn, cursor = abrir_conexion()
    try:
        query = "SELECT * FROM libros"
        cursor.execute(query)
        resultados = cursor.fetchall()
        return resultados
    except mysql.connector.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        cerrar_conexion(conn, cursor)
"""



""" 
Se abren y cierran conexiones pero cuando se hace el COMMIT?
el comportamiento depende de si estás utilizando transacciones explícitas y cómo gestionas el
 commit y rollback. Vamos a analizar los escenarios posibles:

 1. Transacciones Implícitas (Auto-commit Habilitado)
Por defecto, muchas bibliotecas de base de datos, incluyendo mysql.connector, trabajan en modo
 auto-commit. Esto significa que:

Cada operación (INSERT, UPDATE, DELETE) se confirma automáticamente tan pronto como se ejecuta
 exitosamente. Si ocurre un error después de ejecutar una operación, esa operación ya estará
   confirmada y no podrás revertirla, porque el commit ya se realizó.
En este caso, incluso si no cierras la conexión correctamente, los cambios ya estarán impactados
 en la base de datos.

2. Transacciones Explícitas (Auto-commit Deshabilitado)
Si deshabilitas el auto-commit utilizando conn.autocommit = False, las transacciones no se confirman
 automáticamente. En este modo:

Debes realizar un conn.commit() explícito para guardar los cambios en la base.
Si ocurre un error en el programa antes de ejecutar conn.commit(), puedes llamar a conn.rollback()
 para revertir todos los cambios realizados durante esa transacción.
En el contexto de un pool de conexiones:

Si no gestionas la transacción correctamente y devuelves la conexión al pool sin confirmar (o revertir),
 el pool puede reutilizar esa conexión, pero la transacción previa quedará sin confirmar, lo que
 puede causar problemas en la próxima operación.

¿Qué sucede si ocurre un error antes de cerrar la conexión?
Con Auto-commit Habilitado (Por Defecto):

Los cambios ya estarán confirmados en la base de datos y no podrán revertirse.
La conexión quedará en el pool y podrá ser reutilizada, pero no impactará en la transacción porque
 ya fue confirmada.
Con Auto-commit Deshabilitado:

Los cambios no se confirmarán hasta que hagas un conn.commit().
Si no cierras la conexión correctamente, la transacción quedará abierta y puede causar problemas al 
reutilizar la conexión en el pool. Algunos pools intentan revertir automáticamente las transacciones 
abiertas cuando una conexión vuelve al pool, pero esto no es garantizado y depende de la configuración
 del pool.


def modificar_datos():
    conn = None
    cursor = None
    try:
        # Obtener conexión del pool
        conn = obtener_conexion()
        if not conn:
            raise Exception("No se pudo obtener conexión del pool")
        
        # Deshabilitar auto-commit para gestionar transacciones
        conn.autocommit = False
        cursor = conn.cursor()

        # Realizar operaciones
        cursor.execute("INSERT INTO libros (titulo, autor) VALUES ('Libro X', 'Autor Y')")
        cursor.execute("UPDATE libros SET autor = 'Autor Z' WHERE id = 1")
        
        # Confirmar cambios
        conn.commit()
        print("Transacción realizada correctamente.")
    
    except Exception as e:
        # Revertir transacciones si ocurre un error
        if conn:
            conn.rollback()
        print(f"Error durante la transacción: {e}")
    
    finally:
        # Cerrar cursor y devolver conexión al pool
        cerrar_conexion(conn, cursor)

"""