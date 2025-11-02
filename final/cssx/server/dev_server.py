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
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from tradc import TraductorCSSHTML

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cssx-dev-server')

# Configuración de la aplicación Flask
# Obtener el directorio base (donde están los archivos generados)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
app = Flask(__name__, static_folder=BASE_DIR)
socketio = SocketIO(app)

# Variable global para el archivo CSSX
ARCHIVO_CSSX = 'mi_estilo.cssx'

# Ruta para servir el HTML generado
@app.route('/')
def serve_html():
    return send_from_directory(BASE_DIR, 'index.html')

# Ruta para servir el CSS generado
@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css')

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
        if event.src_path.endswith('.cssx'):
            # Evitar procesamiento múltiple del mismo evento
            current_time = time.time()
            if self.last_processed and current_time - self.last_processed < self.processing_delay:
                return
            self.last_processed = current_time
            
            logger.info(f"Archivo CSSX modificado: {event.src_path}")
            
            try:
                # Cambiar al directorio base para la compilación
                old_cwd = os.getcwd()
                os.chdir(BASE_DIR)
                
                # Regenerar CSS y HTML usando el traductor directamente
                logger.info("Recompilando CSSX a CSS y HTML...")
                ruta_cssx = os.path.basename(event.src_path)
                resultado = self.traductor.traducir_desde_archivo(
                    ruta_cssx, 
                    tipo_salida="completo",
                    guardar_css="style.css",
                    guardar_html="index.html"
                )
                css_resultado, html_resultado = resultado['css'], resultado['html']
                
                # Verificar que los archivos se generaron correctamente
                css_path = os.path.join(BASE_DIR, "style.css")
                html_path = os.path.join(BASE_DIR, "index.html")
                
                if os.path.exists(css_path) and os.path.exists(html_path):
                    css_time = os.path.getmtime(css_path)
                    html_time = os.path.getmtime(html_path)
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
            finally:
                # Restaurar el directorio original
                os.chdir(old_cwd)
                self.socketio.emit('error_compilation', {'message': error_msg})

# Función para configurar el observador de archivos
def start_file_observer(socketio):
    logger.info("Iniciando observador de archivos...")
    event_handler = ChangeHandler(socketio)
    observer = Observer()
    # Monitorear el directorio base donde están los archivos
    logger.info(f"Monitoreando directorio: {BASE_DIR}")
    observer.schedule(event_handler, path=BASE_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Función para realizar la compilación inicial del archivo CSSX
def compile_initial_cssx(archivo_cssx='mi_estilo.cssx'):
    """Compilar el archivo CSSX inicial"""
    logger.info(f"Realizando compilación inicial de {archivo_cssx}...")
    
    # Cambiar al directorio base para la compilación
    old_cwd = os.getcwd()
    os.chdir(BASE_DIR)
    
    try:
        # Usar el mismo traductor que en ChangeHandler
        traductor = TraductorCSSHTML()
        
        # Regenerar CSS y HTML usando el traductor directamente
        resultado = traductor.traducir_desde_archivo(
            archivo_cssx, 
            tipo_salida="completo",
            guardar_css="style.css",
            guardar_html="index.html"
        )
        css_resultado, html_resultado = resultado['css'], resultado['html']
        
        # Verificar que los archivos se generaron correctamente
        css_path = os.path.join(BASE_DIR, "style.css")
        html_path = os.path.join(BASE_DIR, "index.html")
        
        if os.path.exists(css_path) and os.path.exists(html_path):
            logger.info("Archivos iniciales generados correctamente.")
            logger.info(f"CSS generado en: {css_path}")
            logger.info(f"HTML generado en: {html_path}")
            return True
        else:
            logger.error("No se pudieron generar los archivos iniciales correctamente.")
            return False
            
    except Exception as e:
        error_msg = f"Error durante la compilación inicial: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return False
    finally:
        # Restaurar el directorio original
        os.chdir(old_cwd)

# Función principal para ejecutar el servidor
def run_server(archivo_cssx='mi_estilo.cssx'):
    global ARCHIVO_CSSX
    ARCHIVO_CSSX = archivo_cssx
    
    # Verificar que el archivo CSSX existe en el directorio base
    archivo_path = os.path.join(BASE_DIR, archivo_cssx)
    if not os.path.exists(archivo_path):
        logger.error(f"El archivo {archivo_cssx} no existe en {BASE_DIR}.")
        return
    
    logger.info(f"Archivo {archivo_cssx} encontrado en {archivo_path}.")
    
    # Realizar la compilación inicial antes de iniciar el servidor
    if not compile_initial_cssx(archivo_cssx):
        logger.warning("La compilación inicial falló, pero intentaremos iniciar el servidor de todas formas.")
    
    # Iniciar observador de archivos en un hilo separado
    observer_thread = threading.Thread(target=start_file_observer, args=(socketio,))
    observer_thread.daemon = True
    observer_thread.start()
    logger.info("Hilo de observación iniciado.")
    
    # Iniciar la aplicación Flask con SocketIO
    logger.info(f"Iniciando servidor en http://localhost:5000 - Usando archivo: {archivo_cssx}")
    socketio.run(app, host='localhost', port=5000, debug=False)

if __name__ == '__main__':
    import sys
    archivo = sys.argv[1] if len(sys.argv) > 1 else 'mi_estilo.cssx'
    run_server(archivo)

