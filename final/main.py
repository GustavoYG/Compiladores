import sys
import os
import json
from cssx.server.dev_server import run_server
from tradc import TraductorCSSHTML
from cssx.semantics.diagnostics import format_diagnostic
from cssx.parser.cssx_parser import parse_to_ast
from cssx.ast.visitor import ASTPrinter

def check_file(archivo_cssx):
    """Realiza análisis semántico de un archivo CSSX"""
    if not os.path.exists(archivo_cssx):
        print(f"Error: El archivo '{archivo_cssx}' no existe")
        return 1
    
    try:
        traductor = TraductorCSSHTML()
        
        # Leer archivo
        with open(archivo_cssx, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Realizar análisis semántico
        diagnosticos = traductor.chequear(contenido, archivo_cssx)
        
        # Mostrar diagnósticos
        if not diagnosticos:
            print(f"✓ {archivo_cssx}: No se encontraron problemas")
            return 0
        
        has_errors = False
        has_warnings = False
        
        for diag in diagnosticos:
            print(format_diagnostic(diag))
            if diag.severity == "ERROR":
                has_errors = True
            elif diag.severity == "WARNING":
                has_warnings = True
        
        # Resumen
        error_count = sum(1 for d in diagnosticos if d.severity == "ERROR")
        warning_count = sum(1 for d in diagnosticos if d.severity == "WARNING")
        
        print(f"\nResumen: {error_count} errores, {warning_count} advertencias")
        
        # Exit code: 1 si hay errores, 0 si solo warnings o sin problemas
        return 1 if has_errors else 0
        
    except Exception as e:
        print(f"Error durante el análisis: {e}")
        return 1

def generate_css_only(archivo_cssx):
    """Genera solo el CSS de un archivo CSSX"""
    if not os.path.exists(archivo_cssx):
        print(f"Error: El archivo '{archivo_cssx}' no existe")
        return 1
    
    try:
        traductor = TraductorCSSHTML()
        
        # Leer archivo
        with open(archivo_cssx, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Generar CSS
        resultado = traductor.traducir_completo(contenido)
        css_content = resultado['css']
        errores = resultado['errores']
        
        # Mostrar CSS
        print(f"=== CSS GENERADO DESDE {archivo_cssx} ===")
        print(css_content)
        
        if errores:
            print(f"\n=== ERRORES ===")
            for error in errores:
                print(f"ERROR: {error}")
        
        return 0
        
    except Exception as e:
        print(f"Error generando CSS: {e}")
        return 1

def show_ast(archivo_cssx):
    """Muestra el AST (árbol sintáctico) de un archivo CSSX"""
    if not os.path.exists(archivo_cssx):
        print(f"Error: El archivo '{archivo_cssx}' no existe")
        return 1
    
    try:
        # Leer archivo
        with open(archivo_cssx, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Generar AST
        ast = parse_to_ast(contenido, archivo_cssx)
        
        # Mostrar AST
        print(f"=== AST (ÁRBOL SINTÁCTICO) DE {archivo_cssx} ===")
        import io
        from contextlib import redirect_stdout
        
        # Capturar la salida del ASTPrinter
        f = io.StringIO()
        with redirect_stdout(f):
            printer = ASTPrinter()
            printer.visit(ast)
        ast_string = f.getvalue()
        
        print(ast_string)
        
        return 0
        
    except Exception as e:
        print(f"Error generando AST: {e}")
        return 1

def analyze_file(archivo_cssx):
    """Análisis completo con diagnósticos y métricas"""
    if not os.path.exists(archivo_cssx):
        print(f"Error: El archivo '{archivo_cssx}' no existe")
        return 1
    
    try:
        traductor = TraductorCSSHTML()
        
        # Leer archivo
        with open(archivo_cssx, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print(f"=== ANÁLISIS COMPLETO DE {archivo_cssx} ===")
        
        # 1. AST
        ast = parse_to_ast(contenido, archivo_cssx)
        print("\n1. AST GENERADO:")
        import io
        from contextlib import redirect_stdout
        
        # Capturar la salida del ASTPrinter
        f = io.StringIO()
        with redirect_stdout(f):
            printer = ASTPrinter()
            printer.visit(ast)
        ast_string = f.getvalue()
        
        print(ast_string[:500] + "..." if len(ast_string) > 500 else ast_string)
        
        # 2. Diagnósticos
        diagnosticos = traductor.chequear(contenido, archivo_cssx)
        print(f"\n2. DIAGNÓSTICOS:")
        if not diagnosticos:
            print("✓ No se encontraron problemas")
            diagnosticos = []  # Asegurar que sea una lista
        else:
            for diag in diagnosticos:
                print(format_diagnostic(diag))
        
        # 3. CSS generado
        resultado = traductor.traducir_completo(contenido)
        css_content = resultado['css']
        print(f"\n3. CSS GENERADO:")
        print(css_content[:300] + "..." if len(css_content) > 300 else css_content)
        
        # 4. Métricas
        error_count = sum(1 for d in (diagnosticos or []) if d.severity == "ERROR")
        warning_count = sum(1 for d in (diagnosticos or []) if d.severity == "WARNING")
        lines_count = len(contenido.splitlines())
        css_length = len(css_content) if css_content else 0
        
        print(f"\n4. MÉTRICAS:")
        print(f"   - Líneas de código: {lines_count}")
        print(f"   - Errores: {error_count}")
        print(f"   - Advertencias: {warning_count}")
        print(f"   - CSS generado: {css_length} caracteres")
        
        return 1 if error_count > 0 else 0
        
    except Exception as e:
        print(f"Error durante el análisis: {e}")
        return 1

def main():
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check" and len(sys.argv) == 3:
            archivo_cssx = sys.argv[2]
            exit_code = check_file(archivo_cssx)
            sys.exit(exit_code)
        elif sys.argv[1] == "--css" and len(sys.argv) == 3:
            archivo_cssx = sys.argv[2]
            exit_code = generate_css_only(archivo_cssx)
            sys.exit(exit_code)
        elif sys.argv[1] == "--ast" and len(sys.argv) == 3:
            archivo_cssx = sys.argv[2]
            exit_code = show_ast(archivo_cssx)
            sys.exit(exit_code)
        elif sys.argv[1] == "--analyze" and len(sys.argv) == 3:
            archivo_cssx = sys.argv[2]
            exit_code = analyze_file(archivo_cssx)
            sys.exit(exit_code)
        elif sys.argv[1] in ["--help", "-h"]:
            print("COMPILADOR CSSX - Uso:")
            print("  python main.py                      # Iniciar servidor de desarrollo")
            print("  python main.py --check <archivo>    # Análisis semántico (warnings/errores)")
            print("  python main.py --css <archivo>      # Generar solo CSS")
            print("  python main.py --ast <archivo>      # Mostrar AST (árbol sintáctico)")
            print("  python main.py --analyze <archivo>  # Análisis completo con métricas")
            print("  python main.py --help              # Mostrar esta ayuda")
            print("\nEjemplos:")
            print("  python main.py --check mi_estilo.cssx")
            print("  python main.py --css test_plantillas_final.cssx")
            print("  python main.py --ast prueba_errores.cssx")
            sys.exit(0)
        else:
            print("Argumentos inválidos. Use --help para ver opciones.")
            sys.exit(1)
    
    # Comportamiento por defecto: servidor de desarrollo
    print("Iniciando el sistema de traducción CSSX...")
    try:
        traductor = TraductorCSSHTML()
        ruta_cssx = "mi_estilo.cssx"
        
        # Compilación inicial del archivo CSSX
        print(f"Compilando {ruta_cssx}...")
        resultado = traductor.traducir_desde_archivo(
            ruta_cssx,
            tipo_salida="completo",
            guardar_css="style.css",
            guardar_html="index.html"
        )
        css_resultado, html_resultado = resultado['css'], resultado['html']
        
        print("Compilación completa:")
        print("- CSS guardado en 'style.css'")
        print("- HTML guardado en 'index.html'")
    except Exception as e:
        print(f"Error durante la compilación inicial: {e}")
        return
    
    # Iniciar el servidor de desarrollo
    print("\nIniciando el servidor de desarrollo...")
    run_server()

if __name__ == "__main__":
    main()

