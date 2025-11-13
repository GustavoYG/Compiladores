#!/usr/bin/env python3
"""
Script de prueba para verificar que la compilación CSSX funciona correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from tradc import TraductorCSSHTML
import tempfile

def probar_compilacion():
    """Prueba la compilación de código CSSX"""
    codigo_ejemplo = """@color_primario = #3498db
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

    print("🧪 Probando compilación CSSX...")
    print(f"📝 Código de entrada:\n{codigo_ejemplo}\n")

    traductor = TraductorCSSHTML()
    
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cssx', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(codigo_ejemplo)
            temp_file_path = temp_file.name
        
        # Compilar
        resultado = traductor.traducir_desde_archivo(
            temp_file_path,
            tipo_salida="completo"
        )
        
        print("✅ Compilación exitosa!")
        print(f"📄 Claves en resultado: {list(resultado.keys())}")
        
        if 'css' in resultado:
            print(f"🎨 CSS generado ({len(resultado['css'])} caracteres):")
            print(resultado['css'][:200] + "..." if len(resultado['css']) > 200 else resultado['css'])
            print()
        
        if 'html' in resultado:
            print(f"🌐 HTML generado ({len(resultado['html'])} caracteres):")
            print(resultado['html'][:200] + "..." if len(resultado['html']) > 200 else resultado['html'])
            print()
        
        if 'errores' in resultado and resultado['errores']:
            print(f"⚠️ Warnings encontrados:")
            for error in resultado['errores']:
                print(f"  - {error}")
            print()
        else:
            print("✅ No se encontraron errores")
        
        # Limpiar
        os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la compilación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if probar_compilacion():
        print("🎉 Prueba completada exitosamente!")
        sys.exit(0)
    else:
        print("💥 Prueba falló!")
        sys.exit(1)