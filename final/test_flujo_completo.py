#!/usr/bin/env python3
"""
Prueba final del editor CSSX - Simulación completa del navegador
"""
import sys
import os
import time

# Añadir path
sys.path.append(os.path.dirname(__file__))

from editor_server import CompiladorCSSX

def test_complete_flow():
    """Simula el flujo completo del editor web"""
    
    print("🎯 === PRUEBA COMPLETA DEL EDITOR CSSX ===")
    print()
    
    # Código que se carga por defecto (ejemplo)
    codigo_ejemplo = """@color_primario = #3498db
@color_secundario = #2c3e50
@espaciado = 20px
@radio = 8px

.contenedor {
    ancho = 90%
    ancho_max = 800px
    margen = 0 auto
    relleno = @espaciado
}

encabezado {
    fondo = @color_primario
    color = blanco
    relleno = 30px
    redondeado = @radio
    sombra = 0 2px 10px rgba(0,0,0,0.1)

    titulo1 {
        texto = "Mi Sitio Web"
        tamano = 28px
        peso = bold
        margen = 0
    }
}

.tarjeta {
    fondo = blanco
    relleno = 25px
    margen = @espaciado 0
    redondeado = @radio
    sombra = 0 4px 15px rgba(0,0,0,0.1)
    borde = 1px solid #e1e8ed

    titulo2 {
        texto = "Bienvenido"
        color = @color_secundario
        tamano = 20px
        margen = 0 0 15px
    }

    parrafo {
        texto = "Este es un ejemplo de CSSX en español."
        color = #666
        interlineado = 1.5
        margen = 0 0 20px
    }

    boton {
        texto = "Ver más"
        relleno = 12px 24px
        fondo = @color_primario
        color = blanco
        borde = none
        redondeado = 5px
        cursor = pointer

        .hover {
            fondo = @color_secundario
        }
    }
}"""

    print("📝 Simulando carga del ejemplo en el editor...")
    print(f"📊 Tamaño del código: {len(codigo_ejemplo)} caracteres")
    print(f"📏 Líneas de código: {len(codigo_ejemplo.split('\\n'))} líneas")
    print()
    
    print("⚡ Simulando compilación automática (como en el navegador)...")
    
    # Simular la compilación que hace el servidor
    compilador = CompiladorCSSX()
    
    try:
        start_time = time.time()
        resultado = compilador.compilar_codigo(codigo_ejemplo)
        end_time = time.time()
        
        print(f"⏱️  Tiempo de compilación: {(end_time - start_time)*1000:.1f}ms")
        print()
        
        if resultado['success']:
            print("✅ COMPILACIÓN EXITOSA!")
            print()
            
            # Simular actualización de vista previa
            if resultado.get('html'):
                html_size = len(resultado['html'])
                print(f"🌐 Vista previa actualizada: {html_size} caracteres HTML")
                
                # Mostrar un fragmento del HTML generado
                html_preview = resultado['html'][:200] + "..." if len(resultado['html']) > 200 else resultado['html']
                print(f"📄 Preview HTML: {html_preview}")
                print()
            
            if resultado.get('css'):
                css_size = len(resultado['css'])
                print(f"🎨 CSS generado: {css_size} caracteres")
                
                # Mostrar el CSS generado
                print("📋 CSS completo:")
                print("=" * 50)
                print(resultado['css'])
                print("=" * 50)
                print()
            
            # Mostrar warnings si existen
            if resultado.get('warnings'):
                print("⚠️  Warnings encontrados:")
                for warning in resultado['warnings']:
                    print(f"   - {warning}")
                print()
            else:
                print("✨ Sin warnings - código CSSX perfecto!")
                print()
                
        else:
            print("❌ ERROR EN LA COMPILACIÓN")
            if resultado.get('errors'):
                for error in resultado['errors']:
                    print(f"   💥 {error}")
            print()
    
        print("🎉 FLUJO COMPLETO SIMULADO EXITOSAMENTE")
        print()
        print("📋 Resumen:")
        print(f"   • Compilación: {'✅ Exitosa' if resultado['success'] else '❌ Falló'}")
        print(f"   • HTML generado: {'✅ Sí' if resultado.get('html') else '❌ No'}")
        print(f"   • CSS generado: {'✅ Sí' if resultado.get('css') else '❌ No'}")
        print(f"   • Warnings: {len(resultado.get('warnings', []))}")
        print(f"   • Errores: {len(resultado.get('errors', []))}")
        print()
        
        if resultado['success'] and resultado.get('html') and resultado.get('css'):
            print("🚀 EL EDITOR DEBERÍA FUNCIONAR PERFECTAMENTE EN EL NAVEGADOR!")
            return True
        else:
            print("⚠️  Hay problemas que necesitan resolverse.")
            return False
    
    except Exception as e:
        print(f"💥 EXCEPCIÓN DURANTE LA PRUEBA: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)