#!/usr/bin/env python3
import sys
import os
import tempfile

# Añadir path
sys.path.append(os.path.dirname(__file__))

from editor_server import CompiladorCSSX

def test_compilador():
    codigo = """@color = #3498db
.test { 
    fondo = @color 
    relleno = 10px
}"""

    print("🧪 Probando CompiladorCSSX...")
    print(f"Código: {codigo}")
    
    compilador = CompiladorCSSX()
    
    try:
        resultado = compilador.compilar_codigo(codigo)
        print(f"✅ Success: {resultado['success']}")
        print(f"📋 Keys: {list(resultado.keys())}")
        
        if resultado['errors']:
            print(f"❌ Errors: {resultado['errors']}")
        if resultado['warnings']:
            print(f"⚠️ Warnings: {resultado['warnings']}")
        if resultado.get('css'):
            print(f"🎨 CSS: {resultado['css'][:100]}...")
        if resultado.get('html'):
            print(f"🌐 HTML: {len(resultado['html'])} chars")
            
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_compilador()