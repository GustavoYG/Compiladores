# semantica_propiedades.py
# Base de datos de propiedades CSS con metadatos MDN

from cssx.semantics.types import CSSProperty, CSSValueType
from typing import Dict, Set


# URLs de documentación MDN para propiedades CSS
MDN_BASE_URL = "https://developer.mozilla.org/en-US/docs/Web/CSS/"


def create_css_properties_db() -> Dict[str, CSSProperty]:
    """Crea la base de datos de propiedades CSS con metadatos MDN"""
    
    properties = {}
    
    # === LAYOUT Y DIMENSIONES ===
    properties["width"] = CSSProperty(
        "width",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto", "max-content", "min-content", "fit-content"},
        doc_url=f"{MDN_BASE_URL}width"
    )
    
    properties["height"] = CSSProperty(
        "height",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto", "max-content", "min-content", "fit-content"},
        doc_url=f"{MDN_BASE_URL}height"
    )
    
    properties["max-width"] = CSSProperty(
        "max-width",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"none", "max-content", "min-content", "fit-content"},
        doc_url=f"{MDN_BASE_URL}max-width"
    )
    
    properties["max-height"] = CSSProperty(
        "max-height",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"none", "max-content", "min-content", "fit-content"},
        doc_url=f"{MDN_BASE_URL}max-height"
    )
    
    properties["min-width"] = CSSProperty(
        "min-width",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto", "max-content", "min-content", "fit-content"},
        doc_url=f"{MDN_BASE_URL}min-width"
    )
    
    properties["min-height"] = CSSProperty(
        "min-height",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto", "max-content", "min-content", "fit-content"},
        doc_url=f"{MDN_BASE_URL}min-height"
    )
    
    # === POSICIONAMIENTO ===
    properties["position"] = CSSProperty(
        "position",
        {CSSValueType.KEYWORD},
        {"static", "relative", "absolute", "fixed", "sticky"},
        doc_url=f"{MDN_BASE_URL}position"
    )
    
    properties["top"] = CSSProperty(
        "top",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto"},
        doc_url=f"{MDN_BASE_URL}top"
    )
    
    properties["right"] = CSSProperty(
        "right",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto"},
        doc_url=f"{MDN_BASE_URL}right"
    )
    
    properties["bottom"] = CSSProperty(
        "bottom",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto"},
        doc_url=f"{MDN_BASE_URL}bottom"
    )
    
    properties["left"] = CSSProperty(
        "left",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto"},
        doc_url=f"{MDN_BASE_URL}left"
    )
    
    properties["z-index"] = CSSProperty(
        "z-index",
        {CSSValueType.NUMBER, CSSValueType.KEYWORD},
        {"auto"},
        doc_url=f"{MDN_BASE_URL}z-index"
    )
    
    # === DISPLAY Y VISIBILIDAD ===
    properties["display"] = CSSProperty(
        "display",
        {CSSValueType.KEYWORD},
        {"none", "block", "inline", "inline-block", "flex", "inline-flex", 
         "grid", "inline-grid", "table", "table-cell", "table-row", "contents"},
        doc_url=f"{MDN_BASE_URL}display"
    )
    
    properties["visibility"] = CSSProperty(
        "visibility",
        {CSSValueType.KEYWORD},
        {"visible", "hidden", "collapse"},
        doc_url=f"{MDN_BASE_URL}visibility"
    )
    
    properties["overflow"] = CSSProperty(
        "overflow",
        {CSSValueType.KEYWORD},
        {"visible", "hidden", "scroll", "auto"},
        doc_url=f"{MDN_BASE_URL}overflow"
    )
    
    # === COLORES Y FONDOS ===
    properties["color"] = CSSProperty(
        "color",
        {CSSValueType.COLOR, CSSValueType.FUNCTION},
        {"transparent", "currentcolor"},
        doc_url=f"{MDN_BASE_URL}color"
    )
    
    properties["background-color"] = CSSProperty(
        "background-color",
        {CSSValueType.COLOR, CSSValueType.FUNCTION},
        {"transparent", "currentcolor"},
        doc_url=f"{MDN_BASE_URL}background-color"
    )
    
    properties["background-image"] = CSSProperty(
        "background-image",
        {CSSValueType.URL, CSSValueType.FUNCTION, CSSValueType.KEYWORD},
        {"none"},
        doc_url=f"{MDN_BASE_URL}background-image"
    )
    
    properties["background-size"] = CSSProperty(
        "background-size",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"auto", "cover", "contain"},
        doc_url=f"{MDN_BASE_URL}background-size"
    )
    
    properties["background-position"] = CSSProperty(
        "background-position",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD, CSSValueType.SPACE_LIST},
        {"left", "center", "right", "top", "bottom"},
        doc_url=f"{MDN_BASE_URL}background-position"
    )
    
    properties["background-repeat"] = CSSProperty(
        "background-repeat",
        {CSSValueType.KEYWORD},
        {"repeat", "repeat-x", "repeat-y", "no-repeat", "space", "round"},
        doc_url=f"{MDN_BASE_URL}background-repeat"
    )
    
    # === TIPOGRAFÍA ===
    properties["font-family"] = CSSProperty(
        "font-family",
        {CSSValueType.STRING, CSSValueType.KEYWORD, CSSValueType.COMMA_LIST},
        {"serif", "sans-serif", "monospace", "cursive", "fantasy"},
        doc_url=f"{MDN_BASE_URL}font-family"
    )
    
    properties["font-size"] = CSSProperty(
        "font-size",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large", "smaller", "larger"},
        doc_url=f"{MDN_BASE_URL}font-size"
    )
    
    properties["font-weight"] = CSSProperty(
        "font-weight",
        {CSSValueType.NUMBER, CSSValueType.KEYWORD},
        {"normal", "bold", "bolder", "lighter"},
        doc_url=f"{MDN_BASE_URL}font-weight"
    )
    
    properties["font-style"] = CSSProperty(
        "font-style",
        {CSSValueType.KEYWORD},
        {"normal", "italic", "oblique"},
        doc_url=f"{MDN_BASE_URL}font-style"
    )
    
    properties["text-align"] = CSSProperty(
        "text-align",
        {CSSValueType.KEYWORD},
        {"left", "right", "center", "justify", "start", "end"},
        doc_url=f"{MDN_BASE_URL}text-align"
    )
    
    properties["text-decoration"] = CSSProperty(
        "text-decoration",
        {CSSValueType.KEYWORD},
        {"none", "underline", "overline", "line-through", "blink"},
        doc_url=f"{MDN_BASE_URL}text-decoration"
    )
    
    properties["line-height"] = CSSProperty(
        "line-height",
        {CSSValueType.NUMBER, CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD},
        {"normal"},
        doc_url=f"{MDN_BASE_URL}line-height"
    )
    
    # === MARGEN Y PADDING ===
    for prop in ["margin", "margin-top", "margin-right", "margin-bottom", "margin-left"]:
        properties[prop] = CSSProperty(
            prop,
            {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.KEYWORD, CSSValueType.SPACE_LIST},
            {"auto"},
            doc_url=f"{MDN_BASE_URL}{prop}"
        )
    
    for prop in ["padding", "padding-top", "padding-right", "padding-bottom", "padding-left"]:
        properties[prop] = CSSProperty(
            prop,
            {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.SPACE_LIST},
            set(),
            doc_url=f"{MDN_BASE_URL}{prop}"
        )
    
    # === BORDES ===
    properties["border"] = CSSProperty(
        "border",
        {CSSValueType.LENGTH, CSSValueType.KEYWORD, CSSValueType.COLOR, CSSValueType.SPACE_LIST},
        {"none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"},
        doc_url=f"{MDN_BASE_URL}border"
    )
    
    properties["border-width"] = CSSProperty(
        "border-width",
        {CSSValueType.LENGTH, CSSValueType.KEYWORD},
        {"thin", "medium", "thick"},
        doc_url=f"{MDN_BASE_URL}border-width"
    )
    
    properties["border-style"] = CSSProperty(
        "border-style",
        {CSSValueType.KEYWORD},
        {"none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"},
        doc_url=f"{MDN_BASE_URL}border-style"
    )
    
    properties["border-color"] = CSSProperty(
        "border-color",
        {CSSValueType.COLOR, CSSValueType.FUNCTION},
        {"transparent", "currentcolor"},
        doc_url=f"{MDN_BASE_URL}border-color"
    )
    
    properties["border-radius"] = CSSProperty(
        "border-radius",
        {CSSValueType.LENGTH, CSSValueType.PERCENTAGE, CSSValueType.SPACE_LIST},
        set(),
        doc_url=f"{MDN_BASE_URL}border-radius"
    )
    
    # === FLEXBOX ===
    properties["flex-direction"] = CSSProperty(
        "flex-direction",
        {CSSValueType.KEYWORD},
        {"row", "row-reverse", "column", "column-reverse"},
        doc_url=f"{MDN_BASE_URL}flex-direction"
    )
    
    properties["justify-content"] = CSSProperty(
        "justify-content",
        {CSSValueType.KEYWORD},
        {"flex-start", "flex-end", "center", "space-between", "space-around", "space-evenly"},
        doc_url=f"{MDN_BASE_URL}justify-content"
    )
    
    properties["align-items"] = CSSProperty(
        "align-items",
        {CSSValueType.KEYWORD},
        {"stretch", "flex-start", "flex-end", "center", "baseline"},
        doc_url=f"{MDN_BASE_URL}align-items"
    )
    
    properties["flex-wrap"] = CSSProperty(
        "flex-wrap",
        {CSSValueType.KEYWORD},
        {"nowrap", "wrap", "wrap-reverse"},
        doc_url=f"{MDN_BASE_URL}flex-wrap"
    )
    
    # === EFECTOS ===
    properties["opacity"] = CSSProperty(
        "opacity",
        {CSSValueType.NUMBER},
        set(),
        doc_url=f"{MDN_BASE_URL}opacity"
    )
    
    properties["box-shadow"] = CSSProperty(
        "box-shadow",
        {CSSValueType.LENGTH, CSSValueType.COLOR, CSSValueType.KEYWORD, CSSValueType.SPACE_LIST, CSSValueType.FUNCTION},
        {"none", "inset"},
        doc_url=f"{MDN_BASE_URL}box-shadow"
    )
    
    properties["cursor"] = CSSProperty(
        "cursor",
        {CSSValueType.KEYWORD, CSSValueType.URL},
        {"auto", "default", "pointer", "text", "move", "not-allowed", "grab", "grabbing"},
        doc_url=f"{MDN_BASE_URL}cursor"
    )
    
    properties["transition"] = CSSProperty(
        "transition",
        {CSSValueType.KEYWORD, CSSValueType.LENGTH, CSSValueType.FUNCTION, CSSValueType.SPACE_LIST},
        {"none", "all", "ease", "linear", "ease-in", "ease-out", "ease-in-out"},
        doc_url=f"{MDN_BASE_URL}transition"
    )
    
    return properties


# Base de datos global de propiedades CSS
CSS_PROPERTIES_DB = create_css_properties_db()


def get_property_info(prop_name: str) -> CSSProperty:
    """Obtiene información sobre una propiedad CSS"""
    return CSS_PROPERTIES_DB.get(prop_name.lower())


def is_known_property(prop_name: str) -> bool:
    """Verifica si una propiedad CSS es conocida"""
    return prop_name.lower() in CSS_PROPERTIES_DB


def get_deprecated_properties() -> Set[str]:
    """Retorna el conjunto de propiedades CSS deprecadas"""
    return {name for name, prop in CSS_PROPERTIES_DB.items() if prop.deprecated}


# Propiedades que comúnmente requieren prefijos de vendor
VENDOR_PREFIX_PROPERTIES = {
    'transform',
    'transition',
    'animation',
    'border-radius',
    'box-shadow',
    'linear-gradient',
    'flex',
    'flex-direction',
    'justify-content',
    'align-items',
    'user-select',
    'appearance'
}

# Aliasado para compatibilidad con imports antiguos
VALID_CSS_PROPERTIES = CSS_PROPERTIES_DB
DEPRECATED_PROPERTIES = get_deprecated_properties()

def get_default_value(prop_name: str) -> str:
    """Obtiene el valor por defecto de una propiedad"""
    return "initial"

def get_valid_values(prop_name: str) -> set:
    """Obtiene los valores válidos de una propiedad"""
    prop = get_property_info(prop_name)
    return prop.valid_keywords if prop else set()
