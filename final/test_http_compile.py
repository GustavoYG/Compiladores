#!/usr/bin/env python3
"""
Probar compilación directamente con el servidor
"""

import requests
import json

codigo_test = """@color_primario = #3498db
@color_secundario = #2ecc71

.contenedor {
    fondo = @color_no_definido
    relleno = 20px
}"""

print("🧪 Probando compilación HTTP directa...")
print("=" * 60)
print("Código a compilar:")
print(codigo_test)
print("=" * 60)

try:
    response = requests.post('http://localhost:5001/compile_test', 
                            json={'code': codigo_test},
                            headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        resultado = response.json()
        print("\n✅ Respuesta exitosa del servidor:")
        print(f"   Success: {resultado.get('success')}")
        print(f"   Warnings: {resultado.get('warnings', [])}")
        print(f"   Errors: {resultado.get('errors', [])}")
        print(f"   CSS length: {len(resultado.get('css', ''))}")
        print(f"   HTML length: {len(resultado.get('html', ''))}")
        
        if resultado.get('warnings'):
            print("\n⚠️ WARNINGS CAPTURADOS:")
            for w in resultado['warnings']:
                print(f"   - {w}")
        else:
            print("\n⚠️ NO SE CAPTURARON WARNINGS")
    else:
        print(f"\n❌ Error HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Asegúrate de que el servidor esté corriendo en http://localhost:5001")
