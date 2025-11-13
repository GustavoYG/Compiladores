#!/usr/bin/env python3
"""Probar qué devuelve el traductor para errores y warnings"""

import sys
import os
import tempfile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tradc import TraductorCSSHTML

# Código con error (variable no definida)
codigo_con_warning = """@color_primario = #3498db

.contenedor {
    fondo = @color_no_existe
    relleno = 20px
}"""

# Crear traductor
traductor = TraductorCSSHTML()

# Crear archivo temporal
with tempfile.NamedTemporaryFile(mode='w', suffix='.cssx', delete=False, encoding='utf-8') as f:
    f.write(codigo_con_warning)
    temp_path = f.name

print("=" * 60)
print("🧪 PROBANDO CÓDIGO CON WARNING (variable no definida)")
print("=" * 60)
print("\nCódigo de entrada:")
print(codigo_con_warning)
print("\n" + "=" * 60)

try:
    resultado = traductor.traducir_desde_archivo(temp_path)
    
    print("\n📊 RESULTADO DEL TRADUCTOR:")
    print(f"Keys en resultado: {list(resultado.keys())}")
    print(f"\n✅ Success implícito: {'html' in resultado and 'css' in resultado}")
    print(f"📏 CSS length: {len(resultado.get('css', ''))}")
    print(f"📏 HTML length: {len(resultado.get('html', ''))}")
    print(f"📏 Errores/Warnings: {len(resultado.get('errores', []))}")
    
    if 'errores' in resultado and resultado['errores']:
        print("\n⚠️ ERRORES/WARNINGS ENCONTRADOS:")
        for i, error in enumerate(resultado['errores'], 1):
            print(f"  {i}. {error}")
    else:
        print("\n✅ No se encontraron errores/warnings")
    
    print("\n🎨 CSS generado:")
    print(resultado.get('css', 'NO CSS'))
    
finally:
    os.unlink(temp_path)

print("\n" + "=" * 60)
print("✅ Prueba completada")
