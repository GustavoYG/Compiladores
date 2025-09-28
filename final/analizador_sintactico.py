# analizador_sintactico.py
# Funciones para el análisis sintáctico del código CSSX

import re
from diccionarios import COLORES, DICCIONARIO_CSS, DICCIONARIO_HTML, SELECTORES_HTML_ESTANDAR


def normalizar_valor(valor, variables):
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
        if token.lower() in COLORES:
            nuevos_tokens.append(COLORES[token.lower()])
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


def analizar_linea(linea, variables):
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
            valor_normalizado = normalizar_valor(valor_raw, variables)
            return clave, valor_normalizado
        except ValueError as e:
            # Si hay error con variables, mantener el valor original
            print(f"ADVERTENCIA: {e}")
            return clave, valor_raw

    raise SyntaxError(f"Línea inválida: '{linea}'")


def extraer_bloque(lineas, inicio):
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


def formatear_css(selector, reglas, nivel=0):
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


def parse_bloque_css(lineas, selector=None, variables=None, nivel=0, html_elements=None):
    """
    Parsea un bloque de código CSS con mejor estructura
    """
    if variables is None:
        variables = {}
    if html_elements is None:
        html_elements = []

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
            bloque, i = extraer_bloque(lineas, i)

            # Procesar selector anidado
            if selector and not nuevo_selector.startswith(".") and not nuevo_selector.startswith("#"):
                # Convertir etiquetas personalizadas a selectores válidos
                if nuevo_selector in DICCIONARIO_HTML:
                    # Es una etiqueta HTML válida
                    etiqueta_html = DICCIONARIO_HTML[nuevo_selector]
                    selector_completo = f"{selector} {etiqueta_html}"
                else:
                    # Es una etiqueta personalizada, convertir a clase
                    selector_completo = f"{selector} .{nuevo_selector}"
            else:
                # Convertir etiquetas personalizadas de primer nivel
                if nuevo_selector in DICCIONARIO_HTML:
                    selector_completo = DICCIONARIO_HTML[nuevo_selector]
                elif not nuevo_selector.startswith(".") and not nuevo_selector.startswith("#"):
                    # Verificar si es un selector HTML estándar o debe ser convertido a clase
                    if nuevo_selector in SELECTORES_HTML_ESTANDAR or nuevo_selector.lower() in SELECTORES_HTML_ESTANDAR:
                        selector_completo = nuevo_selector
                    else:
                        # Etiqueta personalizada de primer nivel, convertir a clase
                        selector_completo = f".{nuevo_selector}"
                else:
                    selector_completo = nuevo_selector

            css_hijo = parse_bloque_css(bloque, selector_completo, variables, nivel + 1, html_elements)
            if css_hijo:
                bloques_css.append(css_hijo)

        elif linea == "}":
            break
        else:
            try:
                clave, valor = analizar_linea(linea, variables)
                if clave.startswith("@"):
                    variables[clave] = valor
                elif clave in ["texto", "contenido"]:
                    # Agregar a elementos HTML
                    html_elements.append({
                        "tipo": "texto",
                        "contenido": valor,
                        "selector": selector
                    })
                elif clave == "titulo_pagina":
                    # Esta variable se manejará en el contexto global
                    variables["titulo_pagina"] = valor
                else:
                    prop_css = DICCIONARIO_CSS.get(clave, clave)
                    reglas.append(f"{prop_css}: {valor};")
            except Exception as e:
                print(f"ERROR en línea '{linea}': {e}")
        i += 1

    # Construir CSS
    resultado = ""
    if reglas and selector:
        resultado = formatear_css(selector, reglas, nivel)

    # Agregar bloques hijos
    if bloques_css:
        if resultado:
            resultado += "\n" + "\n".join(bloques_css)
        else:
            resultado = "\n".join(bloques_css)

    return resultado


def extraer_texto_del_bloque(lineas, variables, para_selector=""):
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
                clave, valor = analizar_linea(linea, variables)
                if clave in ["texto", "contenido"]:
                    # Limpiar el valor de comillas extras
                    valor = valor.strip('"').strip("'")
                    textos.append(valor)
            except Exception:
                continue
    
    # Si hay múltiples textos, combinarlos con espacios
    return " ".join(textos) if textos else ""
