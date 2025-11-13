from IPython import get_ipython
from IPython.display import display
import re
import os
import webbrowser
import tempfile
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import http.server
import socketserver
from urllib.parse import urlparse
import socket

class CSSSelectorExtractor:
    """Extrae todos los selectores CSS utilizados en el HTML generado"""

    def __init__(self):
        self.selectores_usados = set()

    def extraer_selectores_de_html(self, html_content):
        """Extrae clases e IDs utilizados en el HTML"""
        selectores = set()

        # Extraer clases
        clases = re.findall(r'class=["\']([^"\']+)["\']', html_content)
        for clase_str in clases:
            for clase in clase_str.split():
                selectores.add(f".{clase}")

        # Extraer IDs
        ids = re.findall(r'id=["\']([^"\']+)["\']', html_content)
        for id_elem in ids:
            selectores.add(f"#{id_elem}")

        # Agregar selectores de etiquetas básicas que siempre se usan
        etiquetas_basicas = re.findall(r'<(\w+)', html_content)
        for etiqueta in etiquetas_basicas:
            selectores.add(etiqueta.lower())

        return selectores

    def es_selector_usado(self, selector, selectores_usados):
        """Verifica si un selector CSS está siendo utilizado"""
        selector = selector.strip()

        # Selectores básicos siempre se mantienen
        selectores_basicos = ['*', 'body', 'html', ':root', ':before', ':after']
        if any(basico in selector for basico in selectores_basicos):
            return True

        # Verificar selectores de clase e ID exactos
        if selector in selectores_usados:
            return True

        # Verificar selectores compuestos (ej: .clase1 .clase2)
        partes_selector = selector.split()
        for parte in partes_selector:
            if parte.startswith('.') or parte.startswith('#'):
                if parte in selectores_usados:
                    return True
            elif parte in selectores_usados:
                return True

        return False

class DeadCodeEliminator:
    """Elimina CSS no utilizado"""

    def __init__(self):
        self.extractor = CSSSelectorExtractor()

    def limpiar_css(self, css_content, html_content):
        """Elimina reglas CSS no utilizadas"""
        selectores_usados = self.extractor.extraer_selectores_de_html(html_content)

        # Dividir CSS en bloques de reglas
        bloques_css = self._dividir_css_en_bloques(css_content)
        css_limpio = []

        reglas_eliminadas = 0
        reglas_totales = 0

        for bloque in bloques_css:
            reglas_totales += 1
            selector = self._extraer_selector_de_bloque(bloque)

            if self.extractor.es_selector_usado(selector, selectores_usados):
                css_limpio.append(bloque)
            else:
                reglas_eliminadas += 1
                print(f"🗑️  Eliminando CSS no usado: {selector}")

        print(f"📊 Resumen: {reglas_eliminadas}/{reglas_totales} reglas eliminadas")
        return '\n\n'.join(css_limpio)

    def _dividir_css_en_bloques(self, css_content):
        """Divide el CSS en bloques individuales de reglas"""
        bloques = []
        lineas = css_content.split('\n')
        bloque_actual = []
        nivel_llaves = 0

        for linea in lineas:
            bloque_actual.append(linea)
            nivel_llaves += linea.count('{') - linea.count('}')

            if nivel_llaves == 0 and bloque_actual:
                bloque_texto = '\n'.join(bloque_actual).strip()
                if bloque_texto:
                    bloques.append(bloque_texto)
                bloque_actual = []

        return bloques

    def _extraer_selector_de_bloque(self, bloque):
        """Extrae el selector principal de un bloque CSS"""
        primera_linea = bloque.split('{')[0].strip()
        return primera_linea

class HotReloadServer:
    """Servidor web con recarga automática"""

    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.server_thread = None

    def encontrar_puerto_libre(self):
        """Encuentra aun puerto libre para el servidor"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def iniciar_servidor(self, directorio):
        """Inicia el servidor web"""
        puerto_libre = self.encontrar_puerto_libre()
        self.port = puerto_libre

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directorio, **kwargs)

        self.server = socketserver.TCPServer(("", self.port), CustomHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        print(f"🌐 Servidor iniciado en http://localhost:{self.port}")
        return f"http://localhost:{self.port}"

    def detener_servidor(self):
        """Detiene el servidor web"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🛑 Servidor detenido")

class FileWatcher(FileSystemEventHandler):
    """Observador de cambios en archivos"""

    def __init__(self, traductor, archivo_cssx, callback=None):
        self.traductor = traductor
        self.archivo_cssx = archivo_cssx
        self.callback = callback
        self.ultimo_cambio = 0

    def on_modified(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith(self.archivo_cssx):
            # Evitar múltiples recargas en poco tiempo
            tiempo_actual = time.time()
            if tiempo_actual - self.ultimo_cambio < 1:
                return

            self.ultimo_cambio = tiempo_actual
            print(f"🔄 Detectado cambio en {self.archivo_cssx}")

            try:
                self.traductor.regenerar_vista_previa()
                if self.callback:
                    self.callback()
                print("✅ Vista previa actualizada")
            except Exception as e:
                print(f"❌ Error al actualizar: {e}")

class TraductorCSSHTML:
    def __init__(self):
        self.colores = {
            # Agregar más colores según necesites
            'rojo': '#ff0000',
            'azul': '#0000ff',
            'verde': '#008000',
            'amarillo': '#ffff00',
            'naranja': '#ffa500',
            'blanco': '#ffffff',
            'negro': '#000000',
            'gris': '#808080'
        }

        self.diccionario_css = {
            'fondo': 'background-color',
            'color': 'color',
            'tamano': 'font-size',
            'fuente': 'font-family',
            'margen': 'margin',
            'relleno': 'padding',
            'ancho': 'width',
            'alto': 'height',
            'borde': 'border',
            'redondeado': 'border-radius',
            'sombra': 'box-shadow',
            'alinear': 'text-align',
            'peso': 'font-weight',
            'decoracion': 'text-decoration',
            'cursor': 'cursor',
            'transicion': 'transition'
        }

        self.diccionario_html = {
            'parrafo': 'p',
            'titulo': 'h1',
            'subtitulo': 'h2',
            'boton': 'button',
            'caja': 'div',
            'enlace': 'a',
            'imagen': 'img',
            'lista': 'ul',
            'elemento': 'li'
        }

        # Nuevas funcionalidades
        self.dead_code_eliminator = DeadCodeEliminator()
        self.hot_reload_server = HotReloadServer()
        self.file_observer = None
        self.archivo_actual = None
        self.directorio_temporal = None
        self.mostrar_en_terminal = False  # Control para mostrar en terminal

    def cargar_archivo_txt(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                return archivo.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
        except Exception as e:
            raise Exception(f"Error al leer el archivo: {e}")

    def guardar_archivo(self, contenido, ruta_archivo):
        try:
            Path(ruta_archivo).parent.mkdir(parents=True, exist_ok=True)
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write(contenido)
            return True
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return False

    def normalizar_valor(self, valor, variables):
        if valor is None:
            return ""

        if valor.startswith("@"):
            if valor in variables:
                return variables[valor]
            else:
                raise ValueError(f"Variable no definida: {valor}")

        if re.search(r'\w+\s*\([^)]+\)', valor):
            return valor

        tokens = valor.split()
        nuevos_tokens = []

        for token in tokens:
            if token.lower() in self.colores:
                nuevos_tokens.append(self.colores[token.lower()])
            elif re.match(r'^\d+(\.\d+)?$', token):
                nuevos_tokens.append(token + "px")
            elif re.match(r'^\d+(\.\d+)?%$', token):
                nuevos_tokens.append(token)
            elif re.match(r'^\d+(\.\d+)?(px|em|rem|vh|vw|pt|pc|in|cm|mm|ex|ch|vmin|vmax|s|ms)$', token):
                nuevos_tokens.append(token)
            else:
                nuevos_tokens.append(token)

        return ' '.join(nuevos_tokens)

    def analizar_linea(self, linea, variables):
        linea = linea.strip()
        patron_general = r'^\s*([@\w\u00C0-\u017F]+)\s*=\s*(.+)$'

        match = re.match(patron_general, linea)
        if match:
            clave = match.group(1).strip()
            valor_raw = match.group(2).strip()

            if (valor_raw.startswith('"') and valor_raw.endswith('"')) or \
               (valor_raw.startswith("'") and valor_raw.endswith("'")):
                valor_raw = valor_raw[1:-1]

            try:
                valor_normalizado = self.normalizar_valor(valor_raw, variables)
                return clave, valor_normalizado
            except ValueError as e:
                print(f"ADVERTENCIA: {e}")
                return clave, valor_raw

        raise SyntaxError(f"Línea inválida: '{linea}'")

    def extraer_bloque(self, lineas, inicio):
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
        if variables is None:
            variables = {}

        html_parts = []
        i = 0

        while i < len(lineas):
            linea = lineas[i].strip()
            if not linea or linea.startswith("#") or linea.startswith("//"):
                i += 1
                continue

            if "{" in linea and "}" not in linea:
                partes = linea.split("{")[0].strip().split()
                etiqueta = partes[0]
                atributos = " ".join(partes[1:]) if len(partes) > 1 else ""

                etiqueta_html = self.diccionario_html.get(etiqueta, etiqueta)

                i += 1
                bloque, i = self.extraer_bloque(lineas, i)

                contenido_interno = self.parse_bloque_html(bloque, variables)

                if atributos:
                    html_parts.append(f"<{etiqueta_html} {atributos}>")
                else:
                    html_parts.append(f"<{etiqueta_html}>")

                if contenido_interno:
                    html_parts.append(contenido_interno)

                html_parts.append(f"</{etiqueta_html}>")

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
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        return self.parse_bloque_css(lineas)

    def traducir_a_html(self, entrada):
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        return self.parse_bloque_html(lineas)

    def traducir_desde_archivo(self, ruta_archivo, tipo_salida="css", guardar_en=None, limpiar_css=True):
        contenido = self.cargar_archivo_txt(ruta_archivo)

        if tipo_salida.lower() == "css":
            css_resultado = self.traducir_a_css(contenido)

            # Aplicar eliminación de código muerto si está habilitada
            if limpiar_css:
                html_resultado = self.traducir_a_html(contenido)
                css_resultado = self.dead_code_eliminator.limpiar_css(css_resultado, html_resultado)

            resultado = css_resultado
        elif tipo_salida.lower() == "html":
            resultado = self.traducir_a_html(contenido)
        else:
            raise ValueError("tipo_salida debe ser 'css' o 'html'")

        if guardar_en:
            self.guardar_archivo(resultado, guardar_en)

        return resultado

    def imprimir_codigo_generado(self, css, html, cssx_original):
        """Imprime el código CSS y HTML generado en la terminal."""
        print("\n" + "="*40)
        print("📄 Código CSSX Original:")
        print("="*40)
        print(cssx_original)
        print("\n" + "="*40)
        print("🎨 Código CSS Generado (Limpio):")
        print("="*40)
        print(css)
        print("\n" + "="*40)
        print("🧱 Código HTML Generado:")
        print("="*40)
        print(html)
        print("="*40 + "\n")


    def regenerar_vista_previa(self, mostrar_en_terminal=False):
        """Regenera la vista previa con el archivo actual"""
        if not self.archivo_actual or not self.directorio_temporal:
            return

        try:
            contenido = self.cargar_archivo_txt(self.archivo_actual)

            # Generar CSS y HTML
            css = self.traducir_a_css(contenido)
            html = self.traducir_a_html(contenido)

            # Aplicar eliminación de CSS no utilizado
            css_limpio = self.dead_code_eliminator.limpiar_css(css, html)

            # Mostrar en terminal si está habilitado
            if mostrar_en_terminal or self.mostrar_en_terminal:
                self.imprimir_codigo_generado(css_limpio, html, contenido)

            # Actualizar archivos
            ruta_css = os.path.join(self.directorio_temporal, "styles.css")
            ruta_html = os.path.join(self.directorio_temporal, "index.html")

            self.guardar_archivo(css_limpio, ruta_css)

            # HTML con auto-refresh
            plantilla_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vista Previa CSSX - Hot Reload</title>
    <link rel="stylesheet" href="styles.css">
    <script>
        // Auto-refresh cada 2 segundos
        setInterval(function() {{
            fetch(window.location.href)
                .then(() => window.location.reload())
                .catch(() => {{}}); // Ignorar errores de red
        }}, 2000);
    </script>
</head>
<body>
    {html}
    <div style="position: fixed; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px;">
        🔄 Hot Reload Activo
    </div>
</body>
</html>"""

            self.guardar_archivo(plantilla_html, ruta_html)

        except Exception as e:
            print(f"Error al regenerar vista previa: {e}")

    def vista_previa_con_hot_reload(self, archivo_cssx, titulo="Vista Previa Hot Reload", mostrar_en_terminal=False):
        """Inicia vista previa con recarga automática"""
        print("🚀 Iniciando vista previa con Hot Reload...")

        # Detener servidor anterior si existe
        self.detener_hot_reload()

        # Configurar archivos y opciones
        self.archivo_actual = archivo_cssx
        self.directorio_temporal = tempfile.mkdtemp()
        self.mostrar_en_terminal = mostrar_en_terminal

        # Generar vista previa inicial
        self.regenerar_vista_previa(mostrar_en_terminal)

        # Iniciar servidor web
        url_servidor = self.hot_reload_server.iniciar_servidor(self.directorio_temporal)

        # Configurar observador de archivos
        file_watcher = FileWatcher(self, archivo_cssx)
        self.file_observer = Observer()
        self.file_observer.schedule(file_watcher, path=os.path.dirname(os.path.abspath(archivo_cssx)), recursive=False)
        self.file_observer.start()

        # Abrir en navegador
        webbrowser.open(f"{url_servidor}/index.html")

        print(f"✅ Hot Reload activo!")
        print(f"📁 Archivo observado: {self.archivo_actual}")
        print(f"🌐 URL: {url_servidor}/index.html")
        if self.mostrar_en_terminal:
            print("🖥️  Salida en terminal: ACTIVADA")
        else:
            print("🖥️  Salida en terminal: DESACTIVADA")
        print("💡 Modifica tu archivo .cssx y los cambios se reflejarán automáticamente")
        print("⚠️  Para detener, ejecuta: traductor.detener_hot_reload()")

        return url_servidor

    def activar_terminal_output(self):
        """Activa la salida en terminal para el hot reload actual"""
        self.mostrar_en_terminal = True
        print("🖥️  ✅ Salida en terminal ACTIVADA")
        if self.archivo_actual:
            self.regenerar_vista_previa(True)

    def desactivar_terminal_output(self):
        """Desactiva la salida en terminal para el hot reload actual"""
        self.mostrar_en_terminal = False
        print("🖥️  ❌ Salida en terminal DESACTIVADA")

    def imprimir_una_vez(self, archivo_cssx=None):
        """Imprime el código generado una vez sin afectar el hot reload"""
        archivo_a_usar = archivo_cssx or self.archivo_actual
        if not archivo_a_usar:
            print("❌ No hay archivo especificado")
            return

        try:
            contenido = self.cargar_archivo_txt(archivo_a_usar)
            css = self.traducir_a_css(contenido)
            html = self.traducir_a_html(contenido)
            css_limpio = self.dead_code_eliminator.limpiar_css(css, html)

            self.imprimir_codigo_generado(css_limpio, html, contenido)
        except Exception as e:
            print(f"❌ Error al imprimir código: {e}")

    def detener_hot_reload(self):
        """Detiene el hot reload y limpia recursos"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            self.file_observer = None

        self.hot_reload_server.detener_servidor()
        print("🛑 Hot Reload detenido")

    def vista_previa_html(self, archivo_cssx, titulo="Vista previa", usar_hot_reload=False):
        """Vista previa estática (versión original)"""
        if usar_hot_reload:
            return self.vista_previa_con_hot_reload(archivo_cssx, titulo)

        contenido = self.cargar_archivo_txt(archivo_cssx)
        css = self.traducir_a_css(contenido)
        html = self.traducir_a_html(contenido)

        # Aplicar eliminación de CSS no utilizado
        css_limpio = self.dead_code_eliminator.limpiar_css(css, html)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".css", mode="w", encoding="utf-8") as temp_css:
            temp_css.write(css_limpio)
            ruta_css = temp_css.name

        plantilla_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    <link rel="stylesheet" href="file://{ruta_css}">
</head>
<body>
    {html}
</body>
</html>"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_html:
            temp_html.write(plantilla_html)
            ruta_html = temp_html.name

        webbrowser.open(f"file://{ruta_html}")



if __name__ == "__main__":
    traductor = TraductorCSSHTML()
    nombre_archivo_cssx = "mi_estilo.cssx"
    traductor.directorio_temporal = "temp_vista_previa"
    traductor.archivo_actual = nombre_archivo_cssx

    # Crear ejemplo si no existe
    if not os.path.exists(nombre_archivo_cssx):
        ejemplo = '''@color = #0af
body {
  fondo = black
  color = white
  fuente = Arial

  parrafo class="msg" {
    texto = "Hola desde CSSX"
    color = @color
    tamano = 22
    alinear = center
  }
}'''
        with open(nombre_archivo_cssx, 'w', encoding='utf-8') as f:
            f.write(ejemplo)
        print("✅ Archivo de ejemplo creado.")

    traductor.vista_previa_con_hot_reload(nombre_archivo_cssx, mostrar_en_terminal=False)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        traductor.detener_hot_reload()
        print("\n🛑 Programa detenido por el usuario.")