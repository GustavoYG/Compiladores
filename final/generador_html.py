# generador_html.py
# Funciones para generar código HTML desde el código CSSX parseado

from analizador_sintactico import analizar_linea, extraer_bloque, extraer_texto_del_bloque
from diccionarios import DICCIONARIO_HTML, SELECTORES_HTML_ESTANDAR


def generar_html_estructurado(lineas, variables=None, nivel=0, es_body=False, selector_actual=""):
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
                    bloque, i = extraer_bloque(lineas, i)
                    html_anidado = generar_html_estructurado(bloque, variables, nivel, es_body=False)
                    if html_anidado:
                        html_parts.append(html_anidado)
                    continue

                # Verificar si es un selector HTML estándar
                if etiqueta_orig in SELECTORES_HTML_ESTANDAR or etiqueta_orig.lower() in SELECTORES_HTML_ESTANDAR:
                    etiqueta = etiqueta_orig
                    atributos = " ".join(partes[1:]) if len(partes) > 1 else ""
                # Traducir etiqueta personalizada a HTML estándar
                elif etiqueta_orig in DICCIONARIO_HTML:
                    etiqueta = DICCIONARIO_HTML[etiqueta_orig]
                    atributos = " ".join(partes[1:]) if len(partes) > 1 else ""
                           
            # Crear selector para el elemento actual
            if selector_actual:
                nuevo_selector_actual = f"{selector_actual} {etiqueta}"
            else:
                nuevo_selector_actual = etiqueta

            # Extraer contenido de texto primero para este elemento específico
            # Extraer contenido de texto para este elemento específico
            i += 1
            bloque, i = extraer_bloque(lineas, i)
            
            # Obtener el texto del bloque actual
            texto_contenido = extraer_texto_del_bloque(bloque, variables, para_selector=nuevo_selector_actual)
            
            # Generar HTML
            html_parts.append(f"{indent}<{etiqueta}{' ' + atributos if atributos else ''}>")
            if texto_contenido:
                html_parts.append(f"{indent}  {texto_contenido}")
            
            # Procesar contenido anidado
            contenido_anidado = generar_html_estructurado(
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
                clave, valor = analizar_linea(linea, variables)
                if clave.startswith("@"):
                    variables[clave] = valor
                elif clave == "titulo_pagina":
                    variables["titulo_pagina"] = valor
            except Exception as e:
                pass

        i += 1

    return "\n".join(html_parts)


def generar_html_completo(css_content, html_body, html_title="Página Generada"):
    """
    Genera la estructura HTML completa
    """
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_title}</title>
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


def traducir_a_html(entrada):
    """
    Traduce el código de entrada a HTML
    """
    lineas = [l.strip() for l in entrada.strip().split('\n')]
    return generar_html_estructurado(lineas, es_body=True)
