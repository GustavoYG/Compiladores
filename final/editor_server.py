from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import threading
import subprocess
import logging
import traceback
import json
import tempfile
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
logger = logging.getLogger('cssx-editor-server')

# Configuración de la aplicación Flask
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=BASE_DIR)
app.config['SECRET_KEY'] = 'cssx_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales
ARCHIVO_CSSX = 'mi_estilo.cssx'

# Ruta para servir el editor (nueva versión)
@app.route('/')
def serve_editor():
    """Servir la interfaz del editor"""
    return send_from_directory(BASE_DIR, 'editor_v2.html')

# Ruta para obtener el código inicial
@app.route('/get_initial_code')
def get_initial_code():
    """Obtener el código del archivo CSSX inicial"""
    try:
        cssx_path = os.path.join(BASE_DIR, ARCHIVO_CSSX)
        if os.path.exists(cssx_path):
            with open(cssx_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return jsonify({'code': code, 'success': True})
        else:
            return jsonify({'code': '', 'success': False, 'message': 'Archivo no encontrado'})
    except Exception as e:
        logger.error(f"Error al leer archivo inicial: {e}")
        return jsonify({'code': '', 'success': False, 'message': str(e)})

# Ruta HTTP para compilar (para debug)
@app.route('/compile_test', methods=['POST'])
def compile_test():
    """Endpoint HTTP para probar compilación sin WebSocket"""
    try:
        data = request.get_json()
        codigo = data.get('code', '')
        
        logger.info("=" * 60)
        logger.info("🔥 SOLICITUD HTTP DE COMPILACIÓN RECIBIDA")
        logger.info(f"   Código length: {len(codigo)}")
        logger.info("=" * 60)
        
        resultado = compilador.compilar_codigo(codigo)
        
        logger.info(f"✅ Resultado: success={resultado['success']}, warnings={len(resultado['warnings'])}")
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error en compile_test: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Ruta para servir el HTML generado original
@app.route('/preview')
def serve_preview():
    """Servir la vista previa original"""
    return send_from_directory(BASE_DIR, 'index.html')

# Ruta para servir el CSS generado
@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css')

# Ruta para servir archivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)

class CompiladorCSSX:
    """Clase para manejar la compilación de CSSX"""
    
    def __init__(self):
        self.traductor = TraductorCSSHTML()
    
    def compilar_codigo(self, codigo_cssx):
        """
        Compilar código CSSX y retornar resultado
        """
        resultado = {
            'success': False,
            'html': '',
            'css': '',
            'errors': [],
            'warnings': [],
            'ast': None
        }
        
        logger.info(f"Iniciando compilación de código CSSX ({len(codigo_cssx)} caracteres)")
        
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cssx', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(codigo_cssx)
                temp_file_path = temp_file.name
            
            logger.info(f"Archivo temporal creado: {temp_file_path}")
            
            try:
                # Capturar stdout para obtener los warnings que se imprimen con print()
                import io
                from contextlib import redirect_stdout
                
                stdout_capture = io.StringIO()
                
                # Compilar usando el traductor (SIN tipo_salida para usar comportamiento por defecto)
                logger.info("Llamando al traductor...")
                
                with redirect_stdout(stdout_capture):
                    resultado_traductor = self.traductor.traducir_desde_archivo(temp_file_path)
                
                # Capturar warnings que se imprimieron en stdout
                captured_output = stdout_capture.getvalue()
                if captured_output:
                    # Extraer líneas que empiezan con "ADVERTENCIA:"
                    for line in captured_output.split('\n'):
                        line = line.strip()
                        if line.startswith('ADVERTENCIA:'):
                            warning_msg = line.replace('ADVERTENCIA:', '').strip()
                            if warning_msg and warning_msg not in resultado['warnings']:
                                resultado['warnings'].append(warning_msg)
                
                logger.info(f"Traductor completado. Keys: {list(resultado_traductor.keys())}")
                logger.info(f"CSS length: {len(resultado_traductor.get('css', ''))}")
                logger.info(f"HTML length: {len(resultado_traductor.get('html', ''))}")
                logger.info(f"Warnings capturados desde stdout: {len(resultado['warnings'])}")
                
                # El traductor siempre devuelve un diccionario con 'css', 'html', 'errores'
                resultado['success'] = True
                resultado['html'] = resultado_traductor.get('html', '')
                resultado['css'] = resultado_traductor.get('css', '')
                
                # Detectar variables no resueltas en el CSS generado (comienzan con @)
                import re
                css_generado = resultado['css']
                variables_no_resueltas = re.findall(r'@\w+', css_generado)
                if variables_no_resueltas:
                    # Eliminar duplicados
                    variables_unicas = list(set(variables_no_resueltas))
                    for var in variables_unicas:
                        warning_msg = f"Variable no definida: {var}"
                        if warning_msg not in resultado['warnings']:
                            resultado['warnings'].append(warning_msg)
                    logger.info(f"Variables no resueltas detectadas en CSS: {variables_unicas}")
                
                # Agregar errores del resultado como warnings también
                if 'errores' in resultado_traductor and resultado_traductor['errores']:
                    resultado['warnings'].extend(resultado_traductor['errores'])
                
                logger.info(f"✅ Compilación exitosa: CSS={len(resultado['css'])} chars, HTML={len(resultado['html'])} chars, Warnings={len(resultado['warnings'])}")
                        
            except Exception as e:
                logger.error(f"Error durante compilación: {str(e)}")
                logger.error(f"Tipo de error: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                resultado['errors'].append(f"Error interno: {str(e)}")
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error creando archivo temporal: {str(e)}")
            resultado['errors'].append(f"Error creando archivo temporal: {str(e)}")
        
        logger.info(f"Compilación finalizada. Success: {resultado['success']}")
        return resultado

# Instancia global del compilador
compilador = CompiladorCSSX()

@socketio.on('connect')
def handle_connect():
    """Manejar conexión de cliente"""
    logger.info(f"Cliente conectado: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión de cliente"""
    logger.info(f"Cliente desconectado: {request.sid}")

@socketio.on('compile_cssx')
def handle_compile_cssx(data):
    """Manejar solicitud de compilación de código CSSX"""
    try:
        codigo = data.get('code', '')
        timestamp = data.get('timestamp', time.time())
        
        logger.info("=" * 60)
        logger.info(f"🔥 SOLICITUD DE COMPILACIÓN RECIBIDA")
        logger.info(f"   Timestamp: {timestamp}")
        logger.info(f"   Código length: {len(codigo)} caracteres")
        logger.info("=" * 60)
        
        if not codigo.strip():
            emit('compilation_error', {
                'message': 'Código vacío',
                'timestamp': timestamp
            })
            return
        
        # Compilar el código
        resultado = compilador.compilar_codigo(codigo)
        
        logger.info(f"📤 ENVIANDO RESULTADO AL CLIENTE:")
        logger.info(f"   Success: {resultado['success']}")
        logger.info(f"   Errors: {len(resultado['errors'])}")
        logger.info(f"   Warnings: {len(resultado['warnings'])}")
        if resultado['warnings']:
            logger.info(f"   Warnings detectados:")
            for w in resultado['warnings']:
                logger.info(f"      - {w}")
        
        # Enviar resultado al cliente
        emit('compilation_result', {
            'success': resultado['success'],
            'html': resultado['html'],
            'css': resultado['css'],
            'errors': resultado['errors'],
            'warnings': resultado['warnings'],
            'timestamp': timestamp
        })
        
        logger.info(f"✅ Compilación completada y enviada - Éxito: {resultado['success']}")
        
    except Exception as e:
        error_msg = f"Error en handle_compile_cssx: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        emit('compilation_error', {
            'message': error_msg,
            'details': traceback.format_exc(),
            'timestamp': data.get('timestamp', time.time())
        })

@socketio.on('save_file')
def handle_save_file(data):
    """Guardar archivo CSSX"""
    try:
        codigo = data.get('code', '')
        nombre_archivo = data.get('filename', 'mi_estilo.cssx')
        
        # Guardar en el directorio base
        ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(codigo)
        
        logger.info(f"Archivo guardado: {ruta_archivo}")
        
        emit('file_saved', {
            'success': True,
            'filename': nombre_archivo,
            'message': f'Archivo {nombre_archivo} guardado exitosamente'
        })
        
    except Exception as e:
        error_msg = f"Error guardando archivo: {str(e)}"
        logger.error(error_msg)
        
        emit('file_saved', {
            'success': False,
            'message': error_msg
        })

@socketio.on('load_file')
def handle_load_file(data):
    """Cargar archivo CSSX"""
    try:
        nombre_archivo = data.get('filename', 'mi_estilo.cssx')
        ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
        
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            emit('file_loaded', {
                'success': True,
                'filename': nombre_archivo,
                'content': contenido
            })
            
            logger.info(f"Archivo cargado: {ruta_archivo}")
        else:
            emit('file_loaded', {
                'success': False,
                'message': f'Archivo {nombre_archivo} no encontrado'
            })
            
    except Exception as e:
        error_msg = f"Error cargando archivo: {str(e)}"
        logger.error(error_msg)
        
        emit('file_loaded', {
            'success': False,
            'message': error_msg
        })

# Manejador de eventos para cambios en archivos (mantener compatibilidad)
class ChangeHandler(FileSystemEventHandler):
    def __init__(self, socketio):
        self.socketio = socketio
        self.traductor = TraductorCSSHTML()
        self.last_processed = None
        self.processing_delay = 0.5

    def on_modified(self, event):
        if event.src_path.endswith('.cssx'):
            current_time = time.time()
            if self.last_processed and current_time - self.last_processed < self.processing_delay:
                return
            self.last_processed = current_time
            
            logger.info(f"Archivo CSSX modificado: {event.src_path}")
            
            try:
                old_cwd = os.getcwd()
                os.chdir(BASE_DIR)
                
                ruta_cssx = os.path.basename(event.src_path)
                resultado = self.traductor.traducir_desde_archivo(
                    ruta_cssx,
                    guardar_css="style.css",
                    guardar_html="index.html"
                )
                
                # El traductor siempre devuelve css, html, errores - nunca 'exitoso'
                if resultado and 'css' in resultado and 'html' in resultado:
                    self.socketio.emit('file_changed', {
                        'filename': ruta_cssx,
                        'success': True
                    })
                    logger.info("Archivo recompilado exitosamente")
                else:
                    self.socketio.emit('file_changed', {
                        'filename': ruta_cssx,
                        'success': False,
                        'error': 'Error en la generación de CSS/HTML'
                    })
                    
            except Exception as e:
                error_msg = f"Error recompilando archivo: {str(e)}"
                logger.error(error_msg)
                self.socketio.emit('file_changed', {
                    'filename': event.src_path,
                    'success': False,
                    'error': error_msg
                })
            finally:
                os.chdir(old_cwd)

def start_file_observer(socketio):
    """Iniciar observador de archivos"""
    logger.info("Iniciando observador de archivos...")
    event_handler = ChangeHandler(socketio)
    observer = Observer()
    observer.schedule(event_handler, path=BASE_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def run_editor_server(archivo_cssx='mi_estilo.cssx', puerto=5000):
    """Ejecutar servidor del editor"""
    global ARCHIVO_CSSX
    ARCHIVO_CSSX = archivo_cssx
    
    # Verificar archivo CSSX
    archivo_path = os.path.join(BASE_DIR, archivo_cssx)
    if not os.path.exists(archivo_path):
        logger.warning(f"El archivo {archivo_cssx} no existe, se creará uno vacío")
        with open(archivo_path, 'w', encoding='utf-8') as f:
            f.write('// Archivo CSSX vacío\n')
    
    # Iniciar observador de archivos en hilo separado
    observer_thread = threading.Thread(target=start_file_observer, args=(socketio,))
    observer_thread.daemon = True
    observer_thread.start()
    
    logger.info(f"Iniciando Editor CSSX en http://localhost:{puerto}")
    logger.info(f"Archivo principal: {archivo_cssx}")
    
    # Ejecutar servidor
    socketio.run(app, host='localhost', port=puerto, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    import sys
    archivo = sys.argv[1] if len(sys.argv) > 1 else 'mi_estilo.cssx'
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    run_editor_server(archivo, puerto)