#!/usr/bin/env python3
"""
Script para probar el endpoint de compilación del servidor
"""
import requests
import json

def test_server_compilation():
    print("🧪 Probando endpoint de compilación del servidor...")
    
    codigo_test = """@color_primario = #3498db
@espaciado = 20px

.contenedor {
    fondo = @color_primario
    relleno = @espaciado
    redondeado = 8px
    color = blanco
}

titulo1 {
    texto = "Mi Página Web"
    tamano = 24px
    peso = bold
}"""

    # Datos que se envían desde el navegador
    data = {
        'code': codigo_test,
        'timestamp': 1234567890
    }
    
    try:
        # Intentar hacer una petición HTTP POST al endpoint
        url = 'http://localhost:5001/socket.io/'
        print(f"🌐 Conectando a: {url}")
        
        # Primero verificar que el servidor esté corriendo
        response = requests.get('http://localhost:5001/', timeout=5)
        if response.status_code == 200:
            print("✅ Servidor respondiendo correctamente")
            print(f"📄 Tamaño de respuesta: {len(response.text)} chars")
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está corriendo en puerto 5001?")
    except requests.exceptions.Timeout:
        print("⏰ Timeout conectando al servidor")
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_server_compilation()