#from IPython import get_ipython
#from IPython.display import display
import re
import os
import webbrowser
import tempfile
from pathlib import Path


class TraductorCSSHTML:
    def __init__(self):
        # Lista de selectores HTML estándar que no deben convertirse a clases
        self.selectores_html_estandar = [
            "body", "html", "head", "main", "article", "section", "aside", 
            "header", "footer", "nav", "div", "span", "p", "h1", "h2", "h3", 
            "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd", "table", 
            "tr", "td", "th", "thead", "tbody", "tfoot", "form", "input", 
            "button", "select", "option", "textarea", "label", "fieldset", 
            "legend", "a", "img", "iframe", "audio", "video", "canvas", 
            "figure", "figcaption", "blockquote", "pre", "code", "hr"
        ]
        
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

        # Estructura HTML que se va construyendo
        self.html_elements = []
        self.html_title = "Página Generada"

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

        # Si contiene funciones CSS (como rgba, rgb, etc.), devolverlo tal como está
        if re.search(r'\w+\s*\([^)]+\)', valor):
            return valor

        # Convertir colores individuales
        tokens = valor.split()
        nuevos_tokens = []

        for token in tokens:
            # Convertir colores
            if token.lower() in self.colores:
                nuevos_tokens.append(self.colores[token.lower()])
            # Si es un número puro, añadir px
            elif re.match(r'^\d+(\.\d+)?$', token):
                nuevos_tokens.append(token + "px")
            # Si es un porcentaje, mantenerlo
            elif re.match(r'^\d+(\.\d+)?%$', token):
                nuevos_tokens.append(token)
            # Si ya tiene unidad, mantenerlo
            elif re.match(r'^\d+(\.\d+)?(px|em|rem|vh|vw|pt|pc|in|cm|mm|ex|ch|vmin|vmax|s|ms)$', token):
                nuevos_tokens.append(token)
            else:
                nuevos_tokens.append(token)

        return ' '.join(nuevos_tokens)

    def analizar_linea(self, linea, variables):
        """
        Analiza una línea y extrae clave-valor con patrones mejorados
        """
        # Limpiar la línea
        linea = linea.strip()

        # Patrón más flexible que maneja mejor los espacios y caracteres especiales
        patron_general = r'^\s*([@\w\u00C0-\u017F]+)\s*=\s*(.+)$'

        match = re.match(patron_general, linea)
        if match:
            clave = match.group(1).strip()
            valor_raw = match.group(2).strip()

            # Remover comillas si las tiene
            if (valor_raw.startswith('"') and valor_raw.endswith('"')) or \
                    (valor_raw.startswith("'") and valor_raw.endswith("'")):
                valor_raw = valor_raw[1:-1]

            try:
                valor_normalizado = self.normalizar_valor(valor_raw, variables)
                return clave, valor_normalizado
            except ValueError as e:
                # Si hay error con variables, mantener el valor original
                print(f"ADVERTENCIA: {e}")
                return clave, valor_raw

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

    def formatear_css(self, selector, reglas, nivel=0):
        """
        Formatea el CSS con indentación apropiada
        """
        if not reglas:
            return ""

        indent = "  " * nivel
        css = f"{indent}{selector} {{\n"

        for regla in reglas:
            css += f"{indent}  {regla}\n"

        css += f"{indent}}}\n"
        return css

    def parse_bloque_css(self, lineas, selector=None, variables=None, nivel=0):
        """
        Parsea un bloque de código CSS con mejor estructura
        """
        if variables is None:
            variables = {}

        reglas = []
        bloques_css = []

        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if not linea or linea.startswith("#") or linea.startswith("//"):
                i += 1
                continue

            # Detectar selectores anidados
            if "{" in linea and "}" not in linea:
                nuevo_selector = linea.split("{")[0].strip()
                i += 1
                bloque, i = self.extraer_bloque(lineas, i)

                # Procesar selector anidado
                if selector and not nuevo_selector.startswith(".") and not nuevo_selector.startswith("#"):
                    # Convertir etiquetas personalizadas a selectores válidos
                    if nuevo_selector in self.diccionario_html:
                        # Es una etiqueta HTML válida
                        etiqueta_html = self.diccionario_html[nuevo_selector]
                        selector_completo = f"{selector} {etiqueta_html}"
                    else:
                        # Es una etiqueta personalizada, convertir a clase
                        selector_completo = f"{selector} .{nuevo_selector}"
                else:
                    # Convertir etiquetas personalizadas de primer nivel
                    if nuevo_selector in self.diccionario_html:
                        selector_completo = self.diccionario_html[nuevo_selector]
                    elif not nuevo_selector.startswith(".") and not nuevo_selector.startswith("#"):
                        # Verificar si es un selector HTML estándar o debe ser convertido a clase
                        if nuevo_selector in self.selectores_html_estandar or nuevo_selector.lower() in self.selectores_html_estandar:
                            selector_completo = nuevo_selector
                        else:
                            # Etiqueta personalizada de primer nivel, convertir a clase
                            selector_completo = f".{nuevo_selector}"
                    else:
                        selector_completo = nuevo_selector

                css_hijo = self.parse_bloque_css(bloque, selector_completo, variables, nivel + 1)
                if css_hijo:
                    bloques_css.append(css_hijo)

            elif linea == "}":
                break
            else:
                try:
                    clave, valor = self.analizar_linea(linea, variables)
                    if clave.startswith("@"):
                        variables[clave] = valor
                    elif clave in ["texto", "contenido"]:
                        # Agregar a elementos HTML
                        self.html_elements.append({
                            "tipo": "texto",
                            "contenido": valor,
                            "selector": selector
                        })
                    elif clave == "titulo_pagina":
                        self.html_title = valor
                    else:
                        prop_css = self.diccionario_css.get(clave, clave)
                        reglas.append(f"{prop_css}: {valor};")
                except Exception as e:
                    print(f"ERROR en línea '{linea}': {e}")
            i += 1

        # Construir CSS
        resultado = ""
        if reglas and selector:
            resultado = self.formatear_css(selector, reglas, nivel)

        # Agregar bloques hijos
        if bloques_css:
            if resultado:
                resultado += "\n" + "\n".join(bloques_css)
            else:
                resultado = "\n".join(bloques_css)

        return resultado

    def generar_html_estructurado(self, lineas, variables=None, nivel=0, es_body=False, selector_actual=""):
        """
        Genera HTML estructurado desde el código parseado
        """
        if variables is None:
            variables = {}

        html_parts = []
        indent = "  " * nivel
        
        # Variable para controlar si ya se ha generado un elemento body
        hay_body = False
        
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if not linea or linea.startswith("#") or linea.startswith("//"):
                i += 1
                continue

            # Inicializar variables
            etiqueta = ""
            atributos = ""
            bloque = []
            
            # Detectar etiquetas HTML
            if "{" in linea and "}" not in linea:
                # Extraer información de la etiqueta
                partes_linea = linea.split("{")[0].strip()
                
                # Si estamos en el nivel raíz y encontramos un body, marcarlo como ya procesado
                if nivel == 0 and (partes_linea == "body" or partes_linea.lower() == "body") and es_body:
                    hay_body = True

                # Detectar si es una clase o ID
                if partes_linea.startswith("."):
                    etiqueta = "div"
                    clase = partes_linea[1:]
                    atributos = f'class="{clase}"'
                elif partes_linea.startswith("#"):
                    etiqueta = "div"
                    id_elem = partes_linea[1:]
                    atributos = f'id="{id_elem}"'
                else:
                    # Es una etiqueta HTML personalizada o estándar
                    partes = partes_linea.split()
                    etiqueta_orig = partes[0]
                
                    # Si estamos en el nivel principal y es un body, saltarlo si es_body=True
                    if nivel == 0 and (etiqueta_orig == "body" or etiqueta_orig.lower() == "body") and es_body:
                        i += 1
                        bloque, i = self.extraer_bloque(lineas, i)
                        html_anidado = self.generar_html_estructurado(bloque, variables, nivel, es_body=False)
                        if html_anidado:
                            html_parts.append(html_anidado)
                        continue

                    # Verificar si es un selector HTML estándar
                    if etiqueta_orig in self.selectores_html_estandar or etiqueta_orig.lower() in self.selectores_html_estandar:
                        etiqueta = etiqueta_orig
                        atributos = " ".join(partes[1:]) if len(partes) > 1 else ""
                    # Traducir etiqueta personalizada a HTML estándar
                    elif etiqueta_orig in self.diccionario_html:
                        etiqueta = self.diccionario_html[etiqueta_orig]
                        atributos = " ".join(partes[1:]) if len(partes) > 1 else ""
                                   # Crear selector para el elemento actual
                if selector_actual:
                    nuevo_selector_actual = f"{selector_actual} {etiqueta}"
                else:
                    nuevo_selector_actual = etiqueta

                # Extraer contenido de texto primero para este elemento específico
                # Extraer contenido de texto para este elemento específico
                i += 1
                bloque, i = self.extraer_bloque(lineas, i)
                
                # Obtener el texto del bloque actual
                texto_contenido = self.extraer_texto_del_bloque(bloque, variables, para_selector=nuevo_selector_actual)
                
                # Generar HTML
                html_parts.append(f"{indent}<{etiqueta}{' ' + atributos if atributos else ''}>")
                if texto_contenido:
                    html_parts.append(f"{indent}  {texto_contenido}")
                
                # Procesar contenido anidado
                contenido_anidado = self.generar_html_estructurado(
                    bloque, 
                    variables, 
                    nivel + 1, 
                    es_body=False, 
                    selector_actual=nuevo_selector_actual
                )
                
                if contenido_anidado:
                    html_parts.append(contenido_anidado)
                
                html_parts.append(f"{indent}</{etiqueta}>")

            
            elif "=" in linea:
                try:
                    clave, valor = self.analizar_linea(linea, variables)
                    if clave.startswith("@"):
                        variables[clave] = valor
                    elif clave == "titulo_pagina":
                        self.html_title = valor
                except Exception as e:
                    pass

            i += 1

        return "\n".join(html_parts)

    def extraer_texto_del_bloque(self, lineas, variables, para_selector=""):
        """
        Extrae el texto contenido en un bloque, considerando el nivel de anidamiento correcto.
        
        Params:
            lineas: Lista de líneas de código del bloque
            variables: Diccionario de variables definidas
            para_selector: Selector actual para el que se está extrayendo texto
        
        Returns:
            String con el texto encontrado para este elemento
        """
        textos = []
        nivel_actual = 0
        
        for linea in lineas:
            linea = linea.strip()
            
            if "{" in linea:
                nivel_actual += 1
                continue
            elif "}" in linea:
                nivel_actual -= 1
                if nivel_actual < 0:  # Cerrar bloque actual
                    break
                continue
            
            # Solo procesar líneas en el nivel correcto
            if nivel_actual == 0 and "=" in linea:
                try:
                    clave, valor = self.analizar_linea(linea, variables)
                    if clave in ["texto", "contenido"]:
                        # Limpiar el valor de comillas extras
                        valor = valor.strip('"').strip("'")
                        textos.append(valor)
                except Exception:
                    continue
        
        # Si hay múltiples textos, combinarlos con espacios
        return " ".join(textos) if textos else ""
        

    def generar_html_completo(self, css_content, html_body):
        """
        Genera la estructura HTML completa
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.html_title}</title>
  <style>
{css_content}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.min.js"></script>
  <script>
    // Configuración para el hot reload
    document.addEventListener('DOMContentLoaded', function() {{
      // Crear elemento para mostrar errores
      const errorOverlay = document.createElement('div');
      errorOverlay.style.display = 'none';
      errorOverlay.style.position = 'fixed';
      errorOverlay.style.top = '0';
      errorOverlay.style.left = '0';
      errorOverlay.style.right = '0';
      errorOverlay.style.padding = '20px';
      errorOverlay.style.backgroundColor = 'rgba(255, 0, 0, 0.8)';
      errorOverlay.style.color = 'white';
      errorOverlay.style.zIndex = '9999';
      errorOverlay.style.fontSize = '16px';
      errorOverlay.style.fontFamily = 'monospace';
      errorOverlay.style.whiteSpace = 'pre-wrap';
      errorOverlay.style.maxHeight = '50%';
      errorOverlay.style.overflowY = 'auto';
      document.body.appendChild(errorOverlay);
      
      // Conectar al servidor de Socket.IO
      const socket = io();
      
      // Manejar evento de recarga
      socket.on('reload', function() {{
        console.log('Recargando página debido a cambios en el archivo CSSX...');
        location.reload();
      }});
      
      // Manejar evento de error
      socket.on('error_compilation', function(data) {{
        console.error('Error de compilación:', data.message);
        errorOverlay.textContent = 'Error de compilación: ' + data.message;
        errorOverlay.style.display = 'block';
        
        // Ocultar el mensaje de error después de 10 segundos
        setTimeout(function() {{
          errorOverlay.style.display = 'none';
        }}, 10000);
      }});
    }});
  </script>
</head>
<body>
{html_body}
</body>
</html>"""

    def traducir_a_css(self, entrada):
        """
        Traduce el código de entrada a CSS
        """
        self.html_elements = []  # Resetear elementos HTML
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        return self.parse_bloque_css(lineas)

    def traducir_a_html(self, entrada):
        """
        Traduce el código de entrada a HTML
        """
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        return self.generar_html_estructurado(lineas, es_body=True)

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

        # Generar HTML completo
        html_completo = self.generar_html_completo(css_content, html_body)

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

            # Guardar HTML en archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_html:
                temp_html.write(html_completo)
                ruta_html = temp_html.name

            # Abrir en el navegador
            webbrowser.open(f"file://{ruta_html}")
            print(f"Vista previa generada y abierta: {ruta_html}")

        except Exception as e:
            print(f"Error al generar vista previa: {e}")

    def crear_archivo_ejemplo(self, nombre_archivo="ejemplo.cssx"):
        """
        Crea un archivo de ejemplo para probar el traductor
        """
        contenido_ejemplo = '''titulo_pagina = "Mi Página Web"

@color_principal = azul
@fuente_principal = Arial, sans-serif
@tamaño_base = 16

body {
  fondo = @color_principal
  color = blanco
  tamano = @tamaño_base
  margen = 0
  relleno = 20
  fuente = @fuente_principal
  alinear = center
}

parrafo {
  texto = "¡Hola mundo desde mi propio compilador CSS!"
  tamano = 18
  margen = 20 0
}

boton {
  texto = "Haz clic aquí"
  relleno = 10 20
  fondo = naranja
  color = blanco
  borde = none
  redondeado = 5
  cursor = pointer
  tamano = 16
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

  titulo {
    texto = "Este es un título dentro de .caja"
    tamano = 24
    color = rojo
    alinear = center
    peso = bold
    margen = 0 0 15 0
  }

  enlace {
    texto = "Este es un enlace dentro de .caja"
    decoracion = underline
    color = azul
    mostrar = block
    margen = 10 0
  }
}

.boton {
  texto = "Esto es un botón simulado con la clase .boton"
  relleno = 15 25
  fondo = verde
  color = blanco
  redondeado = 8
  margen = 20 auto
  mostrar = inline-block
  cursor = pointer
  transicion = all 0.3s ease
}'''

        self.guardar_archivo(contenido_ejemplo, nombre_archivo)
        print(f"Archivo de ejemplo creado: {nombre_archivo}")
        return nombre_archivo


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