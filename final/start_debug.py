#!/usr/bin/env python3
"""
Script para diagnosticar y solucionar el problema de la vista previa
"""

import sys
import os

# Agregar el directorio al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 DIAGNÓSTICO DEL SISTEMA")
print("=" * 60)

# 1. Verificar que el traductor funciona
print("\n1️⃣ Probando TraductorCSSHTML...")
try:
    from tradc import TraductorCSSHTML
    traductor = TraductorCSSHTML()
    
    # Crear archivo de prueba
    test_code = """@color_primario = #3498db

.contenedor {
    fondo = @color_primario
    relleno = 20px
}"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cssx', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        temp_path = f.name
    
    resultado = traductor.traducir_desde_archivo(temp_path)
    os.unlink(temp_path)
    
    print(f"   ✅ Traductor funciona correctamente")
    print(f"   📊 Keys en resultado: {list(resultado.keys())}")
    print(f"   📏 CSS: {len(resultado.get('css', ''))} chars")
    print(f"   📏 HTML: {len(resultado.get('html', ''))} chars")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Verificar archivos necesarios
print("\n2️⃣ Verificando archivos...")
archivos_necesarios = ['editor.html', 'editor_server.py', 'mi_estilo.cssx']
for archivo in archivos_necesarios:
    if os.path.exists(archivo):
        print(f"   ✅ {archivo} existe")
    else:
        print(f"   ❌ {archivo} NO existe")

# 3. Verificar dependencias
print("\n3️⃣ Verificando dependencias...")
try:
    import flask
    print(f"   ✅ Flask {flask.__version__}")
except:
    print("   ❌ Flask no instalado")

try:
    import flask_socketio
    print(f"   ✅ Flask-SocketIO instalado")
except:
    print("   ❌ Flask-SocketIO no instalado")

try:
    import watchdog
    print(f"   ✅ Watchdog instalado")
except:
    print("   ❌ Watchdog no instalado")

print("\n" + "=" * 60)
print("✅ Diagnóstico completado")
print("\n🚀 Iniciando servidor con logs detallados...")
print("=" * 60 + "\n")

# Ahora iniciar el servidor con logs detallados
os.system(f"{sys.executable} editor_server.py mi_estilo.cssx 5001")
