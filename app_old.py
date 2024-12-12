from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

# Configuración inicial
# Se crea una instancia de la aplicación Flask. Esta instancia es el núcleo de la aplicación
# y manejará las solicitudes y respuestas de la aplicación web. 
# Crea una instancia de Flask. __name__ indica el nombre del módulo actual, 
# lo que permite que Flask sepa dónde buscar recursos y plantillas.
#  Es esencial para inicializar la aplicación.
app = Flask(__name__)

# Conexión a MySQL
# Configuración para conectarse a la base de datos MySQL.
# El diccionario `db_config` almacena los parámetros necesarios para la conexión.
db_config = {
    'host': 'localhost', # Dirección del servidor MySQL (en este caso, localhost)
    'user': 'jconde', # Usuario de la base de datos MySQL
    'password': 'password',  # Contraseña del usuario (reemplazar con la tuya)
    'database': 'libreria'  # Nombre de la base de datos que se va a utilizar      
}

# Conexión a la base de datos utilizando la configuración anterior.
# El doble asterisco (`**`) descompone el diccionario `db_config` en argumentos clave-valor.
# Es equivalente a escribir: mysql.connector.connect(host='localhost', user='root', password='password', database='libreria').
#Esto simplifica el código cuando hay muchos argumentos.
conn = mysql.connector.connect(**db_config)

# Creación de un cursor para ejecutar consultas SQL sobre la base de datos.
cursor = conn.cursor()

# Ruta principal (portada)
# Define la ruta raíz (`/`) de la aplicación. Cuando un usuario accede a esta ruta, 
# Flask ejecutará la función `index` y enviará al cliente el contenido de `index.html`.
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para listar libros
# Define una ruta (`/libros`) para mostrar una lista de libros almacenados en la base de datos.
# Se ejecuta una consulta SQL para obtener todos los registros de la tabla `libros`.
# Los resultados se envían a la plantilla `libros.html` para ser renderizados.
@app.route('/libros')
def libros():
    cursor.execute("SELECT * FROM libros") # Consulta para obtener todos los libros
    libros = cursor.fetchall() # Recupera todos los resultados de la consulta
    return render_template('libros.html', libros=libros) # Renderiza la plantilla con los datos
                    # Renderizar es el proceso de combinar una plantilla HTML con datos dinámicos (pasados desde Flask)
                    #  para generar y entregar al usuario una página web personalizada.

# Ruta para agregar libros
# Define una ruta (`/agregar_libro`) para agregar nuevos libros. 
# Solo permite solicitudes POST, es decir, el formulario de la página debe enviar datos.
@app.route('/agregar_libro', methods=['POST'])
def agregar_libro():
    # Obtiene los datos del formulario enviados por el cliente.
    titulo = request.form['titulo']
    autor = request.form['autor']
    editorial = request.form['editorial']
    precio = request.form['precio']

     # Inserta un nuevo registro en la tabla `libros` con los datos del formulario.
    cursor.execute("INSERT INTO libros (titulo, autor, editorial, precio) VALUES (%s, %s, %s, %s)", 
                   (titulo, autor, editorial, precio))
    
    conn.commit() # Confirma la operación en la base de datos.
    return redirect(url_for('libros')) # Redirige al usuario a la página de listado de libros.

# Ruta para eliminar libros
# Define una ruta (`/eliminar_libro/<int:id>`) para eliminar un libro.
# La parte `<int:id>` captura un número entero (ID) desde la URL.
@app.route('/eliminar_libro/<int:id>')
def eliminar_libro(id):
    # Ejecuta una consulta SQL para eliminar el libro con el ID especificado.
    cursor.execute("DELETE FROM libros WHERE id = %s", (id,))
    conn.commit() # Confirma la operación en la base de datos.
    return redirect(url_for('libros'))


# Ruta para cargar el formulario de edición de un libro
""" 
Ruta: La ruta /editar_libro/<int:id> permite acceder a la página de edición de un libro específico. El <int:id> captura un número entero como parámetro de la URL, que representa el ID del libro.
Consulta: Se ejecuta una consulta SQL para buscar el libro en la base de datos por su ID.
Plantilla: Los datos del libro se pasan a la plantilla editar_libro.html para que puedan mostrarse en un formulario pre-rellenado, listo para ser editado.
"""
@app.route('/editar_libro/<int:id>')
def editar_libro(id):
    cursor.execute("SELECT * FROM libros WHERE id = %s", (id,)) # # Consulta para obtener los datos del libro con el ID especificado
    libro = cursor.fetchone() # Recupera el primer resultado de la consulta (el libro a editar)
    return render_template('editar_libro.html', libro=libro) # Renderiza la plantilla de edición, pasando los datos del libro a la vista

# Ruta para procesar el formulario de edición
""" 
Ruta: La ruta /actualizar_libro/<int:id> se utiliza para procesar los datos enviados desde el formulario de edición. Solo acepta solicitudes HTTP POST.
Recuperación de datos: Se extraen los valores enviados desde el formulario HTML (titulo, autor, editorial, y precio) mediante request.form.
Consulta: La consulta SQL actualiza los datos del libro en la tabla libros usando los nuevos valores proporcionados y el ID del libro.
Confirmación: conn.commit() aplica los cambios en la base de datos.
Redirección: Una vez actualizados los datos, el usuario es redirigido a la lista de libros (/libros).
"""
@app.route('/actualizar_libro/<int:id>', methods=['POST'])# Define la ruta para actualizar un libro, aceptando solo el método POST
def actualizar_libro(id):
    titulo = request.form['titulo'] # Recupera el título enviado desde el formulario
    autor = request.form['autor'] # Recupera el autor enviado desde el formulario
    editorial = request.form['editorial'] # Recupera la editorial enviada desde el formulario
    precio = request.form['precio'] # Recupera el precio enviado desde el formulario
    cursor.execute(
        """
        UPDATE libros
        SET titulo = %s, autor = %s, editorial = %s, precio = %s
        WHERE id = %s
        """, (titulo, autor, editorial, precio, id) 
    ) # Actualiza el registro del libro en la base de datos con los nuevos datos
    conn.commit()  # Confirma los cambios en la base de datos
    return redirect(url_for('libros')) # Redirige al usuario a la lista de libros después de actualizar


# Punto de entrada de la aplicación
# Esta condición asegura que la aplicación se ejecutará solo si el archivo actual 
# es el punto de inicio del programa. Inicia el servidor Flask en modo de depuración.
if __name__ == '__main__':
    app.run(debug=True)
