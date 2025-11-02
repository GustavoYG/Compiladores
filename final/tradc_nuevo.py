# tradc.py
# Traductor CSSX refactorizado - Mantiene la misma interfaz pública

from diccionarios import SELECTORES_HTML_ESTANDAR, COLORES, DICCIONARIO_CSS, DICCIONARIO_HTML
from analizador_sintactico import parse_bloque_css
from generador_css import traducir_a_css
from generador_html import traducir_a_html, generar_html_completo
from gestor_archivos import cargar_archivo_txt, guardar_archivo, vista_previa_html, crear_archivo_ejemplo


class TraductorCSSHTML:
    def __init__(self):
        # Referencias a los diccionarios para mantener compatibilidad
        self.selectores_html_estandar = SELECTORES_HTML_ESTANDAR
        self.colores = COLORES
        self.diccionario_css = DICCIONARIO_CSS
        self.diccionario_html = DICCIONARIO_HTML
        
        # Estructura HTML que se va construyendo
        self.html_elements = []
        self.html_title = "Página Generada"

    def cargar_archivo_txt(self, ruta_archivo):
        """
        Carga el contenido de un archivo de texto plano
        """
        return cargar_archivo_txt(ruta_archivo)

    def guardar_archivo(self, contenido, ruta_archivo):
        """
        Guarda el contenido traducido en un archivo
        """
        return guardar_archivo(contenido, ruta_archivo)

    def traducir_a_css(self, entrada):
        """
        Traduce el código de entrada a CSS
        """
        self.html_elements = []  # Resetear elementos HTML
        return traducir_a_css(entrada)

    def traducir_a_html(self, entrada):
        """
        Traduce el código de entrada a HTML
        """
        return traducir_a_html(entrada)

    def traducir_completo(self, entrada):
        """
        Traduce a CSS y HTML completo
        """
        self.html_elements = []
        self.html_title = "Página Generada"

        # Generar CSS
        css_content = self.traducir_a_css(entrada)

        # Generar HTML del body
        html_body = self.traducir_a_html(entrada)

        # Extraer título de página si está definido
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        variables = {}
        
        # Buscar titulo_pagina en las primeras líneas
        for linea in lineas:
            if "titulo_pagina" in linea and "=" in linea:
                try:
                    from analizador_sintactico import analizar_linea
                    clave, valor = analizar_linea(linea, variables)
                    if clave == "titulo_pagina":
                        self.html_title = valor
                        break
                except:
                    pass

        # Generar HTML completo
        html_completo = generar_html_completo(css_content, html_body, self.html_title)

        return css_content, html_completo

    def traducir_desde_archivo(self, ruta_archivo, tipo_salida="completo", guardar_css=None, guardar_html=None):
        """
        Traduce desde un archivo con opción de salida completa
        """
        contenido = self.cargar_archivo_txt(ruta_archivo)

        if tipo_salida.lower() == "css":
            resultado = self.traducir_a_css(contenido)
            if guardar_css:
                self.guardar_archivo(resultado, guardar_css)
            return resultado
        elif tipo_salida.lower() == "html":
            resultado = self.traducir_a_html(contenido)
            if guardar_html:
                self.guardar_archivo(resultado, guardar_html)
            return resultado
        elif tipo_salida.lower() == "completo":
            css_resultado, html_resultado = self.traducir_completo(contenido)
            if guardar_css:
                self.guardar_archivo(css_resultado, guardar_css)
            if guardar_html:
                self.guardar_archivo(html_resultado, guardar_html)
            return css_resultado, html_resultado
        else:
            raise ValueError("tipo_salida debe ser 'css', 'html' o 'completo'")

    def vista_previa_html(self, archivo_cssx, titulo="Vista previa"):
        """
        Genera automáticamente HTML con CSS traducido y lo abre en el navegador
        """
        try:
            # Cargar y traducir contenido
            contenido = self.cargar_archivo_txt(archivo_cssx)
            css_content, html_completo = self.traducir_completo(contenido)

            # Usar la función del gestor de archivos
            vista_previa_html(archivo_cssx, html_completo, titulo)

        except Exception as e:
            print(f"Error al generar vista previa: {e}")

    def crear_archivo_ejemplo(self, nombre_archivo="ejemplo.cssx"):
        """
        Crea un archivo de ejemplo para probar el traductor
        """
        return crear_archivo_ejemplo(nombre_archivo)


# ==============================================================================
if __name__ == "__main__":
    traductor = TraductorCSSHTML()

    # Crear archivo de ejemplo
    archivo_ejemplo = traductor.crear_archivo_ejemplo("mi_estilo.cssx")

    print("=== EJEMPLO DE TRADUCCIÓN COMPLETA ===")

    try:
        # Traducir desde archivo
        css_resultado, html_resultado = traductor.traducir_desde_archivo(
            archivo_ejemplo,
            tipo_salida="completo",
            guardar_css="styles.css",
            guardar_html="index.html"
        )

        print("\n=== CSS GENERADO ===")
        print(css_resultado)

        print("\n=== HTML GENERADO ===")
        print(html_resultado)

        # Generar vista previa
        print("\n=== GENERANDO VISTA PREVIA ===")
        traductor.vista_previa_html(archivo_ejemplo)

    except Exception as e:
        print(f"Error: {e}")

    # Ejemplo directo también funciona
    print("\n=== EJEMPLO DIRECTO ===")
    ejemplo_directo = '''
    titulo_pagina = "Ejemplo Directo"

    body {
      fondo = negro
      color = blanco
    }

    .contenedor {
      ancho = 300
      alto = 200
      fondo = rojo
      margen = 20 auto
    }

    .contenedor parrafo {
      texto = "Contenido del párrafo"
      color = amarillo
      alinear = center
    }
    '''

    css_directo, html_directo = traductor.traducir_completo(ejemplo_directo)
    print("CSS:")
    print(css_directo)
    print("\nHTML:")
    print(html_directo)
