from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import threading
import subprocess
import logging
import traceback
from datetime import datetime
from tradc import TraductorCSSHTML

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cssx-dev-server')

# Configuración de la aplicación Flask
app = Flask(__name__, static_folder='.')
socketio = SocketIO(app)

# Ruta para servir el HTML generado
@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

# Ruta para servir el CSS generado
@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

# Manejador de eventos para SocketIO
@socketio.on('reload')
def handle_reload_event():
    emit('reload')

# Manejador de eventos para cambios en el sistema de archivos
class ChangeHandler(FileSystemEventHandler):
    def __init__(self, socketio):
        self.socketio = socketio
        self.traductor = TraductorCSSHTML()
        # Evitar procesamiento múltiple del mismo evento
        self.last_processed = None
        self.processing_delay = 0.5  # segundos

    def on_modified(self, event):
        # Verificar si el archivo modificado es el archivo CSSX
        if event.src_path.endswith('mi_estilo.cssx'):
            # Evitar procesamiento múltiple para el mismo archivo en corto tiempo
            current_time = time.time()
            if self.last_processed and current_time - self.last_processed < self.processing_delay:
                logger.debug(f"Ignorando evento demasiado cercano al anterior: {event.src_path}")
                return
            
            self.last_processed = current_time
            logger.info(f"Archivo modificado detectado: {event.src_path}")
            
            try:
                # Regenerar CSS y HTML usando el traductor directamente
                logger.info("Recompilando CSSX a CSS y HTML...")
                ruta_cssx = os.path.basename(event.src_path)
                css_resultado, html_resultado = self.traductor.traducir_desde_archivo(
                    ruta_cssx, 
                    tipo_salida="completo",
                    guardar_css="style.css",
                    guardar_html="index.html"
                )
                
                # Verificar que los archivos se generaron correctamente
                if os.path.exists("style.css") and os.path.exists("index.html"):
                    css_time = os.path.getmtime("style.css")
                    html_time = os.path.getmtime("index.html")
                    current_time = time.time()
                    
                    if current_time - css_time < 5 and current_time - html_time < 5:
                        logger.info("Archivos generados correctamente.")
                        # Emitir evento de recarga
                        self.socketio.emit('reload')
                        logger.info("Evento de recarga enviado al cliente.")
                    else:
                        logger.warning("Archivos generados, pero podrían no estar actualizados.")
                        self.socketio.emit('error_compilation', {'message': 'Los archivos generados podrían no estar actualizados.'})
                else:
                    logger.error("No se pudieron generar los archivos correctamente.")
                    self.socketio.emit('error_compilation', {'message': 'Error al generar archivos.'})
                    
            except Exception as e:
                error_msg = f"Error durante la compilación: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                self.socketio.emit('error_compilation', {'message': error_msg})

# Función para configurar el observador de archivos
def start_file_observer(socketio):
    logger.info("Iniciando observador de archivos...")
    event_handler = ChangeHandler(socketio)
    observer = Observer()
    # Asegurarse de que estamos monitoreando el directorio correcto
    current_dir = os.getcwd()
    logger.info(f"Monitoreando directorio: {current_dir}")
    observer.schedule(event_handler, path=current_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Función para realizar la compilación inicial del archivo CSSX
def compile_initial_cssx():
    logger.info("Realizando compilación inicial de mi_estilo.cssx...")
    try:
        # Usar el mismo traductor que en ChangeHandler
        traductor = TraductorCSSHTML()
        
        # Regenerar CSS y HTML usando el traductor directamente
        ruta_cssx = 'mi_estilo.cssx'
        css_resultado, html_resultado = traductor.traducir_desde_archivo(
            ruta_cssx, 
            tipo_salida="completo",
            guardar_css="style.css",
            guardar_html="index.html"
        )
        
        # Verificar que los archivos se generaron correctamente
        if os.path.exists("style.css") and os.path.exists("index.html"):
            logger.info("Archivos iniciales generados correctamente.")
            return True
        else:
            logger.error("No se pudieron generar los archivos iniciales correctamente.")
            return False
            
    except Exception as e:
        error_msg = f"Error durante la compilación inicial: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return False

# Función principal para ejecutar el servidor
def run_server():
    # Verificar que el archivo CSSX existe
    if not os.path.exists('mi_estilo.cssx'):
        logger.error("El archivo mi_estilo.cssx no existe en el directorio actual.")
        return
    
    logger.info("Archivo mi_estilo.cssx encontrado.")
    
    # Realizar la compilación inicial antes de iniciar el servidor
    if not compile_initial_cssx():
        logger.warning("La compilación inicial falló, pero intentaremos iniciar el servidor de todas formas.")
    
    # Iniciar observador de archivos en un hilo separado
    observer_thread = threading.Thread(target=start_file_observer, args=(socketio,))
    observer_thread.daemon = True
    observer_thread.start()
    logger.info("Hilo de observación iniciado.")
    
    # Iniciar la aplicación Flask con SocketIO
    logger.info("Iniciando servidor en http://localhost:5000")
    socketio.run(app, host='localhost', port=5000, debug=False)

if __name__ == '__main__':
    run_server()

