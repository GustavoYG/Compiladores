# diccionarios.py
# Diccionarios y constantes para el traductor CSSX

# Lista de selectores HTML estándar que no deben convertirse a clases
SELECTORES_HTML_ESTANDAR = [
    "body", "html", "head", "main", "article", "section", "aside", 
    "header", "footer", "nav", "div", "span", "p", "h1", "h2", "h3", 
    "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd", "table", 
    "tr", "td", "th", "thead", "tbody", "tfoot", "form", "input", 
    "button", "select", "option", "textarea", "label", "fieldset", 
    "legend", "a", "img", "iframe", "audio", "video", "canvas", 
    "figure", "figcaption", "blockquote", "pre", "code", "hr"
]

# Diccionario de colores en español a inglés
COLORES = {
    "azul": "blue", "rojo": "red", "verde": "green",
    "blanco": "white", "negro": "black", "amarillo": "yellow",
    "gris": "gray", "naranja": "orange", "morado": "purple",
    "rosa": "pink", "cyan": "cyan", "magenta": "magenta",
    "marron": "brown", "violeta": "violet", "turquesa": "turquoise",
    "dorado": "gold", "plata": "silver", "lima": "lime"
}

# Diccionario de propiedades CSS en español a inglés
DICCIONARIO_CSS = {
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

# Diccionario para etiquetas HTML en español a inglés
DICCIONARIO_HTML = {
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
