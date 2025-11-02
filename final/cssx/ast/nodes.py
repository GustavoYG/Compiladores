# ast_nodos.py
# Definición de nodos AST para CSSX usando dataclasses con slots

from dataclasses import dataclass
from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


@dataclass(slots=True)
class Loc:
    """Información de ubicación en el código fuente"""
    file: str
    line: int
    col: int
    offset: int


@dataclass(slots=True)
class Stylesheet:
    """Nodo raíz del AST que contiene toda la hoja de estilos"""
    children: list  # [RuleSet | AtRule | TemplateDef]
    loc: Loc


@dataclass(slots=True)
class RuleSet:
    """Conjunto de reglas CSS con selectores y declaraciones"""
    selectors: list                # [Selector]
    declarations: list             # [Declaration | TemplateUse] - permite mezclar declaraciones y usos de plantillas
    children: list                 # [RuleSet | AtRule] (para anidamiento)
    loc: Loc


# === SELECTORES ===

@dataclass(slots=True)
class SimpleSelector:
    """Selector simple (tipo, clase, id, atributo, pseudo)"""
    kind: str      # 'type'|'class'|'id'|'attr'|'pseudo'|'pseudo_elem'
    value: str
    loc: Loc


@dataclass(slots=True)
class CompoundSelector:
    """Selector compuesto (múltiples selectores simples sin espacios)"""
    parts: tuple  # tuple[SimpleSelector, ...]
    loc: Loc


@dataclass(slots=True)
class ComplexSelector:
    """Selector complejo con combinadores"""
    left: Union['CompoundSelector', 'ComplexSelector']
    combinator: str    # ' ' | '>' | '+' | '~' | '&'
    right: Union['CompoundSelector', 'ComplexSelector']
    loc: Loc
    
    def specificity(self) -> tuple[int, int, int]:
        """
        Calcula la especificidad CSS según MDN:
        (ids, clases/attrs/pseudo, tipos/pseudo-elem)
        """
        def count_specificity(selector):
            if isinstance(selector, CompoundSelector):
                ids = classes = types = 0
                for part in selector.parts:
                    if part.kind == 'id':
                        ids += 1
                    elif part.kind in ('class', 'attr', 'pseudo'):
                        classes += 1
                    elif part.kind in ('type', 'pseudo_elem'):
                        types += 1
                return (ids, classes, types)
            elif isinstance(selector, ComplexSelector):
                left_spec = count_specificity(selector.left)
                right_spec = count_specificity(selector.right)
                return (left_spec[0] + right_spec[0],
                       left_spec[1] + right_spec[1],
                       left_spec[2] + right_spec[2])
            return (0, 0, 0)
        
        return count_specificity(self)


# === DECLARACIONES Y VALORES ===

@dataclass(slots=True)
class Declaration:
    """Declaración CSS (propiedad: valor)"""
    prop: str
    value: object      # Value
    important: bool
    loc: Loc
    fp: Optional[int] = None   # huella/fingerprint opcional para futuras fusiones


# === JERARQUÍA DE VALORES ===

@dataclass(slots=True)
class ColorLiteral:
    """Color literal (nombre o hex)"""
    name_or_hex: str


@dataclass(slots=True)
class Number:
    """Número sin unidades"""
    n: float


@dataclass(slots=True)
class Dimension:
    """Número con unidades (px, em, rem, etc.)"""
    n: float
    unit: str


@dataclass(slots=True)
class Percentage:
    """Porcentaje"""
    n: float


@dataclass(slots=True)
class Keyword:
    """Palabra clave CSS"""
    name: str


@dataclass(slots=True)
class String:
    """Cadena de texto"""
    text: str


@dataclass(slots=True)
class Url:
    """URL/URI"""
    path: str


@dataclass(slots=True)
class Function:
    """Función CSS (rgb(), calc(), etc.)"""
    name: str
    args: tuple


@dataclass(slots=True)
class SpaceList:
    """Lista de valores separados por espacios"""
    items: tuple


@dataclass(slots=True)
class VariableRef:
    """Referencia a variable (@variable)"""
    name: str


# === AT-RULES Y PLANTILLAS ===

@dataclass(slots=True)
class MediaQuery:
    """Regla @media"""
    query: str
    children: list       # [RuleSet | AtRule]
    loc: Loc


@dataclass(slots=True)
class VariableDecl:
    """Declaración de variable (@nombre = valor)"""
    name: str      # '@variable'  
    value: 'Value'  # Forward reference
    loc: Loc





# === TIPOS DE UNIÓN PARA TYPE HINTS ===


@dataclass(slots=True)
class Param:
    """Parámetro de plantilla"""
    name: str
    default: Optional[object]


@dataclass(slots=True)
class TemplateDef:
    """Definición de plantilla/mixin"""
    name: str
    params: tuple  # tuple[Param, ...]
    body: tuple    # tuple[Declaration, ...]
    loc: Loc


@dataclass(slots=True)
class TemplateUse:
    """Uso/invocación de plantilla"""
    name: str
    args: tuple
    loc: Loc


# === TIPOS DE UNIÓN PARA TYPE HINTS ===

# Selector puede ser cualquiera de estos tipos
Selector = Union[SimpleSelector, CompoundSelector, ComplexSelector]

# Value puede ser cualquiera de estos tipos
Value = Union[
    ColorLiteral, Number, Dimension, Percentage, Keyword,
    String, Url, Function, SpaceList, VariableRef
]


# === PLANTILLAS CSSX ===

@dataclass(slots=True)
class Param:
    """Parámetro de plantilla con valor por defecto opcional"""
    name: str                  # '@parametro'
    default_value: Optional['Value'] = None
    loc: Optional[Loc] = None


@dataclass(slots=True)
class TemplateDef:
    """Definición de plantilla: plantilla NOMBRE(@params) { declarations }"""
    name: str                  # Nombre de la plantilla
    params: list               # [Param] - parámetros con defaults opcionales  
    body: list                 # [Declaration] - declaraciones del cuerpo
    loc: Loc


@dataclass(slots=True)
class TemplateUse:
    """Uso de plantilla: usar NOMBRE(args)"""
    name: str                  # Nombre de la plantilla a usar
    args: list                 # [Value | NamedArg] - argumentos posicionales o nombrados
    loc: Loc


@dataclass(slots=True)
class NamedArg:
    """Argumento nombrado en uso de plantilla: @param=valor"""
    name: str                  # '@parametro'  
    value: 'Value'
    loc: Loc


# AtRule puede ser cualquiera de estos tipos
AtRule = Union[MediaQuery, VariableDecl, TemplateUse]

# Node puede ser cualquier nodo del AST
ASTNode = Union[
    Stylesheet, RuleSet, SimpleSelector, CompoundSelector, ComplexSelector,
    Declaration, ColorLiteral, Number, Dimension, Percentage, Keyword,
    String, Url, Function, SpaceList, VariableRef, MediaQuery,
    VariableDecl, Param, TemplateDef, TemplateUse
]
