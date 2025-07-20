from dev_server import run_server
from tradc import TraductorCSSHTML

def main():
    print("Iniciando el sistema de traducción CSSX...")
    try:
        traductor = TraductorCSSHTML()
        ruta_cssx = "mi_estilo.cssx"
        
        # Compilación inicial del archivo CSSX
        print(f"Compilando {ruta_cssx}...")
        css_resultado, html_resultado = traductor.traducir_desde_archivo(
            ruta_cssx,
            tipo_salida="completo",
            guardar_css="style.css",
            guardar_html="index.html"
        )
        
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

