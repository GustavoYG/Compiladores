# cssx/server/editor.py

from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit
import os
import time
import logging
import traceback
import json

# Adjust the path to import from the root 'cssx' package
from cssx.compiler import Compiler
from cssx.parser.cssx_parser import parse_to_ast
from cssx.lexer.dictionaries import DICCIONARIO_CSS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cssx-editor-server')

# --- Configuration ---
# The server is in cssx/server, so we go up two levels to get to the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

app = Flask(__name__, static_folder=PROJECT_ROOT)
app.config['SECRET_KEY'] = 'cssx_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Compiler Wrapper ---

class EditorCompiler:
    """
    A wrapper for the CSSX compiler to be used by the server.
    """
    def __init__(self):
        self.compiler = Compiler()

    def compile_code(self, code: str):
        """
        Compiles CSSX code and returns a serializable dictionary.
        """
        logger.info(f"Initiating compilation for code of length {len(code)}")
        
        result = self.compiler.compile(code)
        
        # Diagnostics are already serializable dictionaries from the Compiler
        diagnostics = result['diagnostics']
        
        # Separate errors and warnings
        errors = [d for d in diagnostics if d['severity'] == 'ERROR']
        warnings = [d for d in diagnostics if d['severity'] == 'WARNING']

        if errors:
            logger.error(f"CSSX Compilation Errors: {errors}")

        logger.info(f"Compilation finished. Success: {result['success']}, Errors: {len(errors)}, Warnings: {len(warnings)}")

        return {
            'success': result['success'],
            'html': result['html'],
            'css': result['css'],
            'errors': errors,
            'warnings': warnings,
        }

# Global compiler instance
editor_compiler = EditorCompiler()

# --- HTTP Routes ---

@app.route('/')
def serve_editor():
    """Serves the main editor interface."""
    return send_from_directory(PROJECT_ROOT, 'editor_v2.html')

@app.route('/docs')
def serve_docs():
    """Serves the documentation file."""
    return send_from_directory(PROJECT_ROOT, 'documentacion.html')

@app.route('/get_initial_code')
def get_initial_code():
    """Gets the code from the default CSSX file."""
    try:
        cssx_path = os.path.join(PROJECT_ROOT, 'mi_estilo.cssx')
        if os.path.exists(cssx_path):
            with open(cssx_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return jsonify({'code': code, 'success': True})
        else:
            # If the file doesn't exist, create a default one.
            default_code = """
// Welcome to CSSX!
titulo_pagina = "My CSSX Page"

body {
    fondo = #282c34
    color = white
    fuente = "Arial, sans-serif"
    
    .container {
        ancho = 80%
        margen = 20 auto
        relleno = 20
        borde = 1px solid #61dafb
        redondeado = 8px
        
        h1 {
            texto = "Hello, World!"
            color = #61dafb
        }
        
        p {
            texto = "This is a paragraph styled with CSSX."
            tamano = 16
        }
    }
}
"""
            with open(cssx_path, 'w', encoding='utf-8') as f:
                f.write(default_code)
            logger.info(f"Created default file at {cssx_path}")
            return jsonify({'code': default_code, 'success': True})

    except Exception as e:
        logger.error(f"Error reading initial file: {e}")
        return jsonify({'code': '', 'success': False, 'message': str(e)})

@app.route('/get_example_code')
def get_example_code():
    """Gets the code from the 'prueba.cssx' example file."""
    try:
        cssx_path = os.path.join(PROJECT_ROOT, 'prueba.cssx')
        if os.path.exists(cssx_path):
            with open(cssx_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return jsonify({'code': code, 'success': True})
        return jsonify({'code': '// No se encontró prueba.cssx', 'success': False})
    except Exception as e:
        logger.error(f"Error reading example file: {e}")
        return jsonify({'code': '', 'success': False, 'message': str(e)})

@app.route('/get_ast', methods=['POST'])
def get_ast():
    """Parses the code and returns the AST as JSON and as a pretty string."""
    try:
        code = request.get_json().get('code', '')
        if not code.strip():
            return jsonify({'success': False, 'error': 'No code provided.'})
        
        ast = parse_to_ast(code)
        
        ast_dict = ast.to_dict()
        ast_string = ast.to_pretty_string()
        
        return jsonify({'success': True, 'ast': ast_dict, 'ast_string': ast_string})
    except Exception as e:
        logger.error(f"Error generating AST: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_cssx_properties')
def get_cssx_properties():
    """Returns the list of custom CSSX properties."""
    try:
        properties = list(DICCIONARIO_CSS.keys())
        return jsonify({'success': True, 'properties': properties})
    except Exception as e:
        logger.error(f"Error getting CSSX properties: {e}")
        return jsonify({'success': False, 'error': str(e)})

# --- WebSocket Event Handlers ---

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client desconectado: {request.sid}")

@socketio.on('compile_cssx')
def handle_compile_cssx(data):
    """Handles a compilation request from the client."""
    try:
        code = data.get('code', '')
        timestamp = data.get('timestamp', time.time())
        
        logger.info("=" * 60)
        logger.info(f"🔥 COMPILE REQUEST RECEIVED (SID: {request.sid})")
        logger.info(f"   Timestamp: {timestamp}, Code Length: {len(code)}")
        logger.info("=" * 60)
        
        if not code.strip():
            emit('compilation_result', {
                'success': True, 'html': '', 'css': '', 
                'errors': [], 'warnings': [], 'timestamp': timestamp
            })
            return
        
        result = editor_compiler.compile_code(code)
        result['timestamp'] = timestamp
        
        logger.info(f"📤 SENDING RESULT TO CLIENT: Success={result['success']}, Errors={len(result['errors'])}, Warnings={len(result['warnings'])}")
        
        emit('compilation_result', result)
        
    except Exception as e:
        error_msg = f"Internal Server Error in handle_compile_cssx: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        emit('compilation_error', {
            'message': error_msg,
            'details': traceback.format_exc(),
            'timestamp': data.get('timestamp', time.time())
        })

@socketio.on('save_file')
def handle_save_file(data):
    """Saves the provided code to a file."""
    try:
        code = data.get('code', '')
        filename = data.get('filename', 'mi_estilo.cssx')
        
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError("Invalid filename.")

        file_path = os.path.join(PROJECT_ROOT, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        logger.info(f"File saved: {file_path}")
        emit('file_saved', {'success': True, 'filename': filename})
        
    except Exception as e:
        error_msg = f"Error saving file: {str(e)}"
        logger.error(error_msg)
        emit('file_saved', {'success': False, 'message': error_msg})

# --- Server Runner ---

def run_server(port=5000):
    """Runs the Flask-SocketIO development server."""
    logger.info(f"Starting CSSX Editor Server on http://localhost:{port}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    socketio.run(app, host='localhost', port=port, debug=False)

if __name__ == '__main__':
    run_server()