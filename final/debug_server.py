#!/usr/bin/env python3

import sys
import os
import logging
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('debug-server')

# Importar el traductor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tradc import TraductorCSSHTML

app = Flask(__name__)
app.config['SECRET_KEY'] = 'debug-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# HTML simplificado para debug
DEBUG_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Debug CSSX</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <h1>Debug CSSX Compiler</h1>
    <div>
        <h2>Input CSSX:</h2>
        <textarea id="code" rows="10" cols="60">@color_primario = #3498db

.contenedor {
    fondo = @color_primario
    relleno = 20px
}</textarea>
        <br><br>
        <button onclick="compileCode()">Compilar</button>
    </div>
    
    <div>
        <h2>Output:</h2>
        <div id="output" style="border: 1px solid #ccc; padding: 10px; white-space: pre-wrap;"></div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', function() {
            console.log('🟢 Conectado al servidor');
            document.getElementById('output').innerHTML = '🟢 Conectado al servidor\\n';
        });

        socket.on('compilation_result', function(data) {
            console.log('📄 Resultado recibido:', data);
            const output = document.getElementById('output');
            output.innerHTML = `✅ Compilación exitosa!
Success: ${data.success}
CSS: ${data.css}
HTML: ${data.html}
Errores: ${JSON.stringify(data.errors)}
Warnings: ${JSON.stringify(data.warnings)}
`;
        });

        socket.on('compilation_error', function(data) {
            console.log('❌ Error recibido:', data);
            document.getElementById('output').innerHTML = `❌ Error: ${data.message}`;
        });

        function compileCode() {
            const code = document.getElementById('code').value;
            console.log('📤 Enviando código:', code);
            socket.emit('compile_cssx', {
                code: code,
                timestamp: Date.now()
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return DEBUG_HTML

@socketio.on('connect')
def test_connect():
    logger.info('Cliente conectado')
    emit('server_message', {'message': 'Conectado al servidor debug'})

@socketio.on('compile_cssx')
def handle_compile_cssx(data):
    logger.info(f'📨 Recibida solicitud de compilación: {data}')
    
    try:
        codigo = data.get('code', '')
        timestamp = data.get('timestamp', 0)
        
        logger.info(f'📝 Código a compilar: {repr(codigo[:100])}...')
        
        if not codigo.strip():
            emit('compilation_error', {
                'message': 'Código vacío',
                'timestamp': timestamp
            })
            return
        
        # Crear traductor
        traductor = TraductorCSSHTML()
        logger.info('🔧 Traductor creado')
        
        # Crear archivo temporal
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cssx', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(codigo)
            temp_file_path = temp_file.name
        
        logger.info(f'📁 Archivo temporal: {temp_file_path}')
        
        # Compilar
        resultado_traductor = traductor.traducir_desde_archivo(temp_file_path)
        logger.info(f'🎯 Resultado del traductor: {list(resultado_traductor.keys())}')
        logger.info(f'🎨 CSS length: {len(resultado_traductor.get("css", ""))}')
        logger.info(f'🌐 HTML length: {len(resultado_traductor.get("html", ""))}')
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        # Enviar resultado
        resultado = {
            'success': True,
            'html': resultado_traductor.get('html', ''),
            'css': resultado_traductor.get('css', ''),
            'errors': [],
            'warnings': resultado_traductor.get('errores', []),
            'timestamp': timestamp
        }
        
        logger.info(f'📤 Enviando resultado: success={resultado["success"]}, CSS={len(resultado["css"])}, HTML={len(resultado["html"])}')
        emit('compilation_result', resultado)
        
    except Exception as e:
        logger.error(f'❌ Error durante compilación: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        
        emit('compilation_error', {
            'message': f'Error: {str(e)}',
            'timestamp': data.get('timestamp', 0)
        })

if __name__ == '__main__':
    port = 5002
    logger.info(f'🚀 Iniciando servidor debug en puerto {port}')
    socketio.run(app, host='0.0.0.0', port=port, debug=True)