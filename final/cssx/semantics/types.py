# types.py
# Tipos de datos semánticos y validaciones básicas

from enum import Enum
from typing import Union, Any, Set, List
from cssx.ast.nodes import *
import re


class CSSValueType(Enum):
    """Tipos de valores CSS"""
    COLOR = "color"
    LENGTH = "length"
    PERCENTAGE = "percentage"
    NUMBER = "number"
    KEYWORD = "keyword"
    STRING = "string"
    URL = "url"
    FUNCTION = "function"
    VARIABLE = "variable"
    SPACE_LIST = "space_list"
    COMMA_LIST = "comma_list"
    UNKNOWN = "unknown"


class CSSProperty:
    """Información sobre una propiedad CSS"""
    
    def __init__(self, name: str, accepted_types: Set[CSSValueType], 
                 keywords: Set[str] = None, deprecated: bool = False,
                 doc_url: str = None):
        self.name = name
        self.accepted_types = accepted_types
        self.keywords = keywords or set()
        self.deprecated = deprecated
        self.doc_url = doc_url
    
    def accepts_type(self, value_type: CSSValueType) -> bool:
        """Verifica si la propiedad acepta este tipo de valor"""
        return value_type in self.accepted_types
    
    def accepts_keyword(self, keyword: str) -> bool:
        """Verifica si la propiedad acepta esta palabra clave"""
        return keyword.lower() in {k.lower() for k in self.keywords}


def get_value_type(value: Any) -> CSSValueType:
    """Determina el tipo de un valor AST"""
    if isinstance(value, ColorLiteral):
        return CSSValueType.COLOR
    elif isinstance(value, Dimension):
        return CSSValueType.LENGTH
    elif isinstance(value, Percentage):
        return CSSValueType.PERCENTAGE
    elif isinstance(value, Number):
        return CSSValueType.NUMBER
    elif isinstance(value, Keyword):
        return CSSValueType.KEYWORD
    elif isinstance(value, String):
        return CSSValueType.STRING
    elif isinstance(value, Url):
        return CSSValueType.URL
    elif isinstance(value, Function):
        return CSSValueType.FUNCTION
    elif isinstance(value, VariableRef):
        return CSSValueType.VARIABLE
    elif isinstance(value, SpaceList):
        return CSSValueType.SPACE_LIST
    else:
        return CSSValueType.UNKNOWN


def is_valid_color(value: str) -> bool:
    """Verifica si un valor es un color válido"""
    # Colores hexadecimales
    if re.match(r'^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$', value):
        return True
    
    # Colores con nombre (CSS básicos)
    css_colors = {
        'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 
        'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 
        'teal', 'aqua', 'orange', 'transparent', 'currentcolor'
    }
    
    return value.lower() in css_colors


def is_valid_length_unit(unit: str) -> bool:
    """Verifica si una unidad de longitud es válida"""
    length_units = {
        # Unidades absolutas
        'px', 'pt', 'pc', 'in', 'cm', 'mm',
        # Unidades relativas
        'em', 'rem', 'ex', 'ch', 'vh', 'vw', 'vmin', 'vmax', '%',
        # Unidades de tiempo
        's', 'ms'
    }
    return unit.lower() in length_units


def is_valid_css_identifier(name: str) -> bool:
    """Verifica si un identificador CSS es válido"""
    # Patrón CSS extendido: debe empezar con letra, guión o guión bajo
    # y puede contener letras (incluyendo unicode), números, guiones y guiones bajos
    return re.match(r'^[a-zA-Z_\u00C0-\u017F-][a-zA-Z0-9_\u00C0-\u017F-]*$', name) is not None


def is_vendor_prefixed(property_name: str) -> bool:
    """Verifica si una propiedad tiene prefijo de vendor"""
    vendor_prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
    return any(property_name.startswith(prefix) for prefix in vendor_prefixes)


def get_standard_property_name(property_name: str) -> str:
    """Obtiene el nombre estándar de una propiedad (sin prefijo de vendor)"""
    vendor_prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
    for prefix in vendor_prefixes:
        if property_name.startswith(prefix):
            return property_name[len(prefix):]
    return property_name


def validate_selector(selector: str) -> List[str]:
    """Valida un selector CSS y retorna lista de problemas encontrados"""
    problems = []
    
    # Verificar caracteres inválidos básicos
    if not selector.strip():
        problems.append("Selector vacío")
        return problems
    
    # Verificar patrones problemáticos
    if selector.startswith('.') and '.' in selector[1:]:
        if not re.match(r'^\.[a-zA-Z_-][a-zA-Z0-9_-]*(\.[a-zA-Z_-][a-zA-Z0-9_-]*)*$', selector):
            problems.append("Múltiples clases deben estar correctamente separadas")
    
    # Verificar IDs múltiples (problemático)
    if selector.count('#') > 1:
        problems.append("Múltiples IDs en un selector no es válido")
    
    # Verificar combinadores consecutivos
    combinators = [' ', '>', '+', '~']
    for i, combinator in enumerate(combinators):
        for j, other in enumerate(combinators):
            if i != j and f"{combinator}{other}" in selector:
                problems.append(f"Combinadores consecutivos '{combinator}{other}' no son válidos")
    
    return problems


class SemanticContext:
    """Contexto semántico durante el análisis"""
    
    def __init__(self):
        self.variables: dict[str, Any] = {}
        self.current_file: str = "<unknown>"
        self.in_media_query: bool = False
        self.current_selector_specificity: tuple[int, int, int] = (0, 0, 0)
    
    def set_variable(self, name: str, value: Any, loc: Loc = None):
        """Define una variable en el contexto"""
        self.variables[name] = {
            'value': value,
            'defined_at': loc,
            'used': False
        }
    
    def get_variable(self, name: str) -> Any:
        """Obtiene una variable del contexto"""
        if name in self.variables:
            self.variables[name]['used'] = True
            return self.variables[name]['value']
        return None
    
    def has_variable(self, name: str) -> bool:
        """Verifica si una variable está definida"""
        return name in self.variables
    
    def use_variable(self, name: str, loc: Loc = None):
        """Marca una variable como usada"""
        if name in self.variables:
            self.variables[name]['used'] = True
    
    def get_unused_variables(self) -> List[tuple[str, Loc]]:
        """Retorna variables no utilizadas"""
        unused = []
        for name, info in self.variables.items():
            if not info['used'] and info['defined_at']:
                unused.append((name, info['defined_at']))
        return unused
