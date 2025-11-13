import re
import os
from pathlib import Path

class TraductorCSSHTML:
    def __init__(self):
        self.colores = {
            "azul": "blue", "rojo": "red", "verde": "green",
            "blanco": "white", "negro": "black", "amarillo": "yellow",
            "gris": "gray", "naranja": "orange", "morado": "purple",
            "rosa": "pink", "cyan": "cyan", "magenta": "magenta",
            "marron": "brown", "violeta": "violet", "turquesa": "turquoise",
            "dorado": "gold", "plata": "silver", "lima": "lime"
        }

        self.diccionario_css = {
            # Colores y fondo
            "fondo": "background-color",
            "color_fondo": "background-color",
            "imagen_fondo": "background-image",
            "posicion_fondo": "background-position",
            "repetir_fondo": "background-repeat",
            "tamaño_fondo": "background-size",
            "fondo_adjunto": "background-attachment",

            # Tipografía
            "color": "color",
            "tamano": "font-size",
            "tamaño": "font-size",
            "fuente": "font-family",
            "grosor": "font-weight",
            "peso": "font-weight",
            "estilo_texto": "font-style",
            "alinear": "text-align",
            "alinear_texto": "text-align",
            "decoracion": "text-decoration",
            "decoracion_texto": "text-decoration",
            "mayusculas": "text-transform",
            "transformar_texto": "text-transform",
            "espacio_entre_letras": "letter-spacing",
            "espacio_letras": "letter-spacing",
            "altura_linea": "line-height",
            "interlineado": "line-height",
            "sombra_texto": "text-shadow",

            # Layout general
            "ancho": "width",
            "anchura": "width",
            "alto": "height",
            "altura": "height",
            "mostrar": "display",
            "ubicacion": "position",
            "posicion": "position",
            "arriba": "top",
            "abajo": "bottom",
            "izquierda": "left",
            "derecha": "right",
            "orden": "z-index",
            "indice_z": "z-index",
            "desbordamiento": "overflow",
            "visible": "visibility",
            "visibilidad": "visibility",
            "medir": "box-sizing",
            "flotante": "float",
            "limpiar": "clear",

            # Margen y padding
            "margen": "margin",
            "margen_arriba": "margin-top",
            "margen_abajo": "margin-bottom",
            "margen_izquierda": "margin-left",
            "margen_derecha": "margin-right",

            "relleno": "padding",
            "relleno_arriba": "padding-top",
            "relleno_abajo": "padding-bottom",
            "relleno_izquierda": "padding-left",
            "relleno_derecha": "padding-right",

            # Bordes
            "borde": "border",
            "borde_arriba": "border-top",
            "borde_abajo": "border-bottom",
            "borde_izquierdo": "border-left",
            "borde_derecho": "border-right",
            "color_borde": "border-color",
            "tipo_borde": "border-style",
            "estilo_borde": "border-style",
            "grosor_borde": "border-width",
            "ancho_borde": "border-width",
            "redondeado": "border-radius",
            "radio_borde": "border-radius",

            # Flexbox
            "direccion": "flex-direction",
            "direccion_flex": "flex-direction",
            "alinear_elementos": "justify-content",
            "justificar": "justify-content",
            "alinear_contenido": "align-items",
            "alinear_items": "align-items",
            "envolver": "flex-wrap",
            "envolver_flex": "flex-wrap",
            "crecer": "flex-grow",
            "crecer_flex": "flex-grow",
            "achicar": "flex-shrink",
            "encoger": "flex-shrink",
            "base": "flex-basis",
            "base_flex": "flex-basis",
            "alinear_self": "align-self",
            "orden_flex": "order",

            # Grid
            "columnas": "grid-template-columns",
            "filas": "grid-template-rows",
            "areas": "grid-template-areas",
            "espacio_columnas": "grid-column-gap",
            "espacio_filas": "grid-row-gap",
            "espacio_grid": "grid-gap",
            "area": "grid-area",
            "columna_inicio": "grid-column-start",
            "columna_fin": "grid-column-end",
            "fila_inicio": "grid-row-start",
            "fila_fin": "grid-row-end",

            # Efectos visuales
            "cursor": "cursor",
            "opacidad": "opacity",
            "transicion": "transition",
            "animacion": "animation",
            "sombra": "box-shadow",
            "sombra_caja": "box-shadow",
            "filtro": "filter",
            "transformar": "transform",
            "perspectiva": "perspective",
            "clip": "clip-path",

            # Responsive
            "ancho_min": "min-width",
            "ancho_max": "max-width",
            "alto_min": "min-height",
            "alto_max": "max-height",

            # Otros
            "contenido": "content",
            "lista_estilo": "list-style",
            "lista_tipo": "list-style-type",
            "lista_posicion": "list-style-position",
            "lista_imagen": "list-style-image",
            "outline": "outline",
            "resize": "resize",
            "user_select": "user-select"
        }

        # Diccionario para etiquetas HTML
        self.diccionario_html = {
            "titulo": "h1",
            "titulo2": "h2",
            "titulo3": "h3",
            "titulo4": "h4",
            "titulo5": "h5",
            "titulo6": "h6",
            "parrafo": "p",
            "enlace": "a",
            "imagen": "img",
            "division": "div",
            "seccion": "section",
            "articulo": "article",
            "encabezado": "header",
            "pie": "footer",
            "navegacion": "nav",
            "lista": "ul",
            "lista_ordenada": "ol",
            "elemento": "li",
            "tabla": "table",
            "fila": "tr",
            "celda": "td",
            "encabezado_tabla": "th",
            "cuerpo_tabla": "tbody",
            "encabezado_tabla_completo": "thead",
            "pie_tabla": "tfoot",
            "formulario": "form",
            "entrada": "input",
            "boton": "button",
            "etiqueta": "label",
            "seleccionar": "select",
            "opcion": "option",
            "textarea": "textarea",
            "span": "span",
            "fuerte": "strong",
            "enfasis": "em",
            "codigo": "code",
            "preformateado": "pre",
            "cita": "blockquote",
            "linea": "hr",
            "salto": "br",
            "contenedor": "div",
            "video": "video",
            "audio": "audio",
            "canvas": "canvas"
        }

    def cargar_archivo_txt(self, ruta_archivo):
        """
        Carga el contenido de un archivo de texto plano
        """
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                return archivo.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
        except Exception as e:
            raise Exception(f"Error al leer el archivo: {e}")

    def guardar_archivo(self, contenido, ruta_archivo):
        """
        Guarda el contenido traducido en un archivo
        """
        try:
            # Crear directorio si no existe
            Path(ruta_archivo).parent.mkdir(parents=True, exist_ok=True)

            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write(contenido)
            return True
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return False

    def normalizar_valor(self, valor, variables):
        """
        Normaliza los valores CSS, convirtiendo colores y añadiendo unidades
        """
        if valor is None:
            return ""

        # Manejar variables
        if valor.startswith("@"):
            if valor in variables:
                return variables[valor]
            else:
                raise ValueError(f"Variable no definida: {valor}")

        # Convertir colores
        if valor.lower() in self.colores:
            return self.colores[valor.lower()]

        # Procesar valores múltiples y añadir unidades px a números
        tokens = re.split(r'\s+|(?<!\d)[/](?!\d)', valor)
        nuevos_tokens = []

        for token in tokens:
            # Si es un número puro, añadir px
            if re.match(r'^\d+(\.\d+)?$', token):
                nuevos_tokens.append(token + "px")
            # Si es un porcentaje, mantenerlo
            elif re.match(r'^\d+(\.\d+)?%$', token):
                nuevos_tokens.append(token)
            # Si ya tiene unidad, mantenerlo
            elif re.match(r'^\d+(\.\d+)?(px|em|rem|vh|vw|pt|pc|in|cm|mm|ex|ch|vmin|vmax)$', token):
                nuevos_tokens.append(token)
            else:
                nuevos_tokens.append(token)

        return ' '.join(nuevos_tokens)

    def analizar_linea(self, linea, variables):
        """
        Analiza una línea y extrae clave-valor
        """
        # Patrón mejorado para reconocer diferentes formatos
        patrones = [
            r'^\s*([@a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"([^"]*)"\s*$',  # clave = "valor"
            r'^\s*([@a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\'([^\']*)\'\s*$',  # clave = 'valor'
            r'^\s*([@a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(@[a-zA-Z_][a-zA-Z0-9_]*)\s*$',  # clave = @variable
            r'^\s*([@a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^"\'\s][^\s]*)\s*$',  # clave = valor_sin_comillas
        ]

        for patron in patrones:
            match = re.match(patron, linea.strip())
            if match:
                clave = match.group(1)
                valor = match.group(2)
                valor_normalizado = self.normalizar_valor(valor, variables)
                return clave, valor_normalizado

        raise SyntaxError(f"Línea inválida: '{linea}'")

    def extraer_bloque(self, lineas, inicio):
        """
        Extrae un bloque de código delimitado por llaves
        """
        nivel = 1
        fin = inicio
        while fin < len(lineas) and nivel > 0:
            l = lineas[fin]
            if "{" in l:
                nivel += l.count("{")
            if "}" in l:
                nivel -= l.count("}")
            fin += 1
        return lineas[inicio:fin - 1], fin

    def parse_bloque_css(self, lineas, selector=None, padre=None, variables=None):
        """
        Parsea un bloque de código CSS
        """
        if variables is None:
            variables = {}
        reglas = []
        hijos = []

        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if not linea or linea.startswith("#") or linea.startswith("//"):
                i += 1
                continue

            if "{" in linea and "}" not in linea:
                nuevo_selector = linea.split("{")[0].strip()
                i += 1
                bloque, i = self.extraer_bloque(lineas, i)
                hijo_css = self.parse_bloque_css(bloque, nuevo_selector, nuevo_selector, variables)
                if hijo_css:
                    hijos.append(hijo_css)
            elif linea == "}":
                break
            else:
                try:
                    clave, valor = self.analizar_linea(linea, variables)
                    if clave.startswith("@"):
                        variables[clave] = valor
                    else:
                        prop_css = self.diccionario_css.get(clave, clave)
                        reglas.append(f"  {prop_css}: {valor};")
                except Exception as e:
                    print(f"ERROR en línea '{linea}': {e}")
            i += 1

        # Construir el CSS final
        resultado = ""
        if reglas and selector:
            resultado = f"{selector} {{\n" + "\n".join(reglas) + "\n}"

        if hijos:
            if resultado:
                resultado += "\n\n" + "\n\n".join(hijos)
            else:
                resultado = "\n\n".join(hijos)

        return resultado

    def parse_bloque_html(self, lineas, variables=None):
        """
        Parsea un bloque de código HTML
        """
        if variables is None:
            variables = {}

        html_parts = []
        i = 0

        while i < len(lineas):
            linea = lineas[i].strip()
            if not linea or linea.startswith("#") or linea.startswith("//"):
                i += 1
                continue

            # Detectar etiquetas HTML
            if "{" in linea and "}" not in linea:
                # Extraer nombre de etiqueta y atributos
                partes = linea.split("{")[0].strip().split()
                etiqueta = partes[0]
                atributos = " ".join(partes[1:]) if len(partes) > 1 else ""

                # Traducir nombre de etiqueta
                etiqueta_html = self.diccionario_html.get(etiqueta, etiqueta)

                i += 1
                bloque, i = self.extraer_bloque(lineas, i)

                # Procesar contenido interno
                contenido_interno = self.parse_bloque_html(bloque, variables)

                # Construir etiqueta HTML
                if atributos:
                    html_parts.append(f"<{etiqueta_html} {atributos}>")
                else:
                    html_parts.append(f"<{etiqueta_html}>")

                if contenido_interno:
                    html_parts.append(contenido_interno)

                html_parts.append(f"</{etiqueta_html}>")

            # Detectar texto plano o contenido
            elif "=" in linea:
                try:
                    clave, valor = self.analizar_linea(linea, variables)
                    if clave.startswith("@"):
                        variables[clave] = valor
                    elif clave == "texto" or clave == "contenido":
                        html_parts.append(valor)
                except Exception as e:
                    html_parts.append(linea)
            else:
                html_parts.append(linea)

            i += 1

        return "\n".join(html_parts)

    def traducir_a_css(self, entrada):
        """
        Traduce el código de entrada a CSS
        """
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        return self.parse_bloque_css(lineas)

    def traducir_a_html(self, entrada):
        """
        Traduce el código de entrada a HTML
        """
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        return self.parse_bloque_html(lineas)

    def traducir_desde_archivo(self, ruta_archivo, tipo_salida="css", guardar_en=None):
        """
        Traduce desde un archivo de texto plano
        """
        contenido = self.cargar_archivo_txt(ruta_archivo)

        if tipo_salida.lower() == "css":
            resultado = self.traducir_a_css(contenido)
        elif tipo_salida.lower() == "html":
            resultado = self.traducir_a_html(contenido)
        else:
            raise ValueError("tipo_salida debe ser 'css' o 'html'")

        if guardar_en:
            self.guardar_archivo(resultado, guardar_en)

        return resultado


# ==============================================================================
if __name__ == "__main__":
    traductor = TraductorCSSHTML()

    # Ejemplo de CSS
    ejemplo_css = '''
    @color_principal = azul
    @fuente_principal = Arial, sans-serif
    @tamaño_base = 16

    body {
      fondo = @color_principal
      color = blanco
      tamano = @tamaño_base
      margen = 0 auto
      relleno = 20
      fuente = @fuente_principal
      alinear = center
    }

    .caja {
      fondo = blanco
      color = negro
      margen = 40 auto
      relleno = 20
      ancho = 80%
      borde = 1px solid gris
      redondeado = 10
      sombra = 0 4px 8px rgba(0,0,0,0.1)

      .titulo {
        tamano = 24
        color = rojo
        alinear = center
        peso = bold
      }

      a {
        decoracion = underline
        color = amarillo
        transicion = color 0.3s ease
      }
    }

    .boton {
      relleno = 10 20
      fondo = naranja
      color = blanco
      redondeado = 5
      cursor = pointer
      borde = none
      transicion = all 0.3s ease
    }
    '''

    # Ejemplo de HTML
    ejemplo_html = '''
    @titulo_principal = "Mi Página Web"
    @descripcion = "Una página de ejemplo"

    division class="container" {
      encabezado {
        titulo {
          texto = @titulo_principal
        }
        parrafo {
          texto = @descripcion
        }
      }

      seccion class="content" {
        parrafo {
          texto = "Este es el contenido principal de la página."
        }
        enlace href="#" {
          texto = "Enlace de ejemplo"
        }
      }

      pie {
        parrafo {
          texto = "© 2024 Mi Sitio Web"
        }
      }
    }
    '''

    print("=== TRADUCCIÓN CSS ===")
    resultado_css = traductor.traducir_a_css(ejemplo_css)
    print(resultado_css)

    print("\n=== TRADUCCIÓN HTML ===")
    resultado_html = traductor.traducir_a_html(ejemplo_html)
    print(resultado_html)

    # Ejemplo de cómo usar con archivos
    print("\n=== EJEMPLO DE USO CON ARCHIVOS ===")
    print("Para usar con archivos:")
    print("traductor.traducir_desde_archivo('mi_archivo.txt', 'css', 'salida.css')")
    print("traductor.traducir_desde_archivo('mi_archivo.txt', 'html', 'salida.html')")