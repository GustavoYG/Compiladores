# cssx/ast/nodes.py
# Definición de nodos AST para CSSX usando dataclasses con slots

import dataclasses
from dataclasses import dataclass, fields
from typing import Union, Optional, List, Tuple

# --- Pretty Printer ---

def to_pretty_string_visitor(node, indent=0):
    if not isinstance(node, Node):
        return '  ' * indent + repr(node)

    name, attrs, children = node._pretty_string_parts()

    indent_str = '  ' * indent
    attr_str = f"({', '.join(attrs)})" if attrs else ""
    
    s = f"{indent_str}{name}{attr_str}"

    for child in children:
        s += '\n' + to_pretty_string_visitor(child, indent + 1)
    
    return s

# --- Base Node for Serialization ---

class Node:
    """Base class for all AST nodes to provide serialization."""
    def to_dict(self):
        """
        Serializes the dataclass instance to a dictionary, handling nested nodes
        and lists of nodes.
        """
        result = {"node_type": self.__class__.__name__}
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, list):
                result[f.name] = [item.to_dict() if isinstance(item, Node) else item for item in value]
            elif isinstance(value, Node):
                result[f.name] = value.to_dict()
            elif isinstance(value, (str, int, float, bool, type(None))):
                result[f.name] = value
            elif isinstance(value, tuple):
                 result[f.name] = [item.to_dict() if isinstance(item, Node) else item for item in value]
            else:
                # For complex types that are not nodes, convert to string
                result[f.name] = str(value)
        return result

    def to_pretty_string(self):
        return to_pretty_string_visitor(self)

    def _pretty_string_parts(self):
        # Generic fallback
        name = self.__class__.__name__
        attrs = []
        children = []
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name == 'loc' and isinstance(value, Loc):
                attrs.append(f"loc: {value.line}:{value.col}")
            elif isinstance(value, list):
                children.extend(value)
            elif isinstance(value, Node):
                children.append(value)
            elif value is not None and not f.name == 'loc':
                attrs.append(f"{f.name}={repr(value)}")
        return name, attrs, children

@dataclass(slots=True)
class Loc(Node):
    """Información de ubicación en el código fuente"""
    file: str
    line: int
    col: int
    offset: int
    def _pretty_string_parts(self):
        return "Loc", [f"{self.line}:{self.col}"], []


# --- Top-Level Structure ---

@dataclass(slots=True)
class Stylesheet(Node):
    """Nodo raíz del AST que contiene toda la hoja de estilos"""
    children: List[Union['RuleSet', 'AtRule', 'TemplateDef']]
    loc: Loc
    def _pretty_string_parts(self):
        return "StyleSheet", [f"loc: {self.loc.line}:{self.loc.col}"], self.children

@dataclass(slots=True)
class RuleSet(Node):
    """Conjunto de reglas CSS con selectores y declaraciones"""
    selectors: List['Selector']
    declarations: List[Union['Declaration', 'TemplateUse']]
    children: List[Union['RuleSet', 'AtRule']]
    loc: Loc
    def _pretty_string_parts(self):
        children = []
        children.extend(self.selectors)
        children.extend(self.declarations)
        children.extend(self.children)
        return "RuleSet", [f"loc: {self.loc.line}:{self.loc.col}"], children

# === Selectors ===

@dataclass(slots=True)
class SimpleSelector(Node):
    """Selector simple (tipo, clase, id, atributo, pseudo)"""
    kind: str
    value: str
    loc: Loc
    def _pretty_string_parts(self):
        return "SimpleSelector", [f"{self.kind}: '{self.value}'"], []

@dataclass(slots=True)
class CompoundSelector(Node):
    """Selector compuesto (múltiples selectores simples sin espacios)"""
    parts: Tuple['SimpleSelector', ...]
    loc: Loc
    def _pretty_string_parts(self):
        return "CompoundSelector", [], self.parts

@dataclass(slots=True)
class ComplexSelector(Node):
    """Selector complejo con combinadores"""
    left: Union['CompoundSelector', 'ComplexSelector']
    combinator: str
    right: Union['CompoundSelector', 'ComplexSelector']
    loc: Loc
    def _pretty_string_parts(self):
        return "ComplexSelector", [f"combinator: '{self.combinator}'"], [self.left, self.right]

# === Declarations and Values ===

@dataclass(slots=True)
class Declaration(Node):
    """Declaración CSS (propiedad: valor)"""
    prop: str
    value: 'Value'
    important: bool
    loc: Loc
    def _pretty_string_parts(self):
        value_type = self.value.__class__.__name__
        return "Declaration", [f"{self.prop}: {value_type}"], [self.value]

# --- Value Hierarchy ---

@dataclass(slots=True)
class ColorLiteral(Node):
    name_or_hex: str
    def _pretty_string_parts(self):
        return "ColorLiteral", [f"'{self.name_or_hex}'"], []

@dataclass(slots=True)
class Number(Node):
    n: float
    def _pretty_string_parts(self):
        return "Number", [str(self.n)], []

@dataclass(slots=True)
class Dimension(Node):
    n: float
    unit: str
    def _pretty_string_parts(self):
        return "Dimension", [f"{self.n}{self.unit}"], []

@dataclass(slots=True)
class Percentage(Node):
    n: float
    def _pretty_string_parts(self):
        return "Percentage", [f"{self.n}%"], []

@dataclass(slots=True)
class Keyword(Node):
    name: str
    def _pretty_string_parts(self):
        return "Keyword", [f"'{self.name}'"], []

@dataclass(slots=True)
class String(Node):
    text: str
    def _pretty_string_parts(self):
        return "String", [f"'{self.text}'"], []

@dataclass(slots=True)
class Url(Node):
    path: str
    def _pretty_string_parts(self):
        return "Url", [f"'{self.path}'"], []

@dataclass(slots=True)
class Function(Node):
    name: str
    args: tuple
    def _pretty_string_parts(self):
        return "Function", [f"name='{self.name}'"], list(self.args)

@dataclass(slots=True)
class SpaceList(Node):
    items: tuple
    def _pretty_string_parts(self):
        return "SpaceList", [], list(self.items)

@dataclass(slots=True)
class VariableRef(Node):
    name: str
    def _pretty_string_parts(self):
        return "VariableRef", [f"'{self.name}'"], []

# --- At-Rules and Templates ---

@dataclass(slots=True)
class MediaQuery(Node):
    """Regla @media"""
    query: str
    children: List[Union['RuleSet', 'AtRule']]
    loc: Loc
    def _pretty_string_parts(self):
        return "MediaQuery", [f"query='{self.query}'"], self.children

@dataclass(slots=True)
class VariableDecl(Node):
    """Declaración de variable (@nombre = valor)"""
    name: str
    value: 'Value'
    loc: Loc
    def _pretty_string_parts(self):
        return "VariableDecl", [f"name='{self.name}'"], [self.value]

@dataclass(slots=True)
class Param(Node):
    """Parámetro de plantilla con valor por defecto opcional"""
    name: str
    default_value: Optional['Value'] = None
    loc: Optional[Loc] = None
    def _pretty_string_parts(self):
        attrs = [f"name='{self.name}'"]
        children = []
        if self.default_value:
            children.append(self.default_value)
        return "Param", attrs, children

@dataclass(slots=True)
class TemplateDef(Node):
    """Definición de plantilla: plantilla NOMBRE(@params) { declarations }"""
    name: str
    params: List[Param]
    body: List[Declaration]
    loc: Loc
    def _pretty_string_parts(self):
        children = []
        children.extend(self.params)
        children.extend(self.body)
        return "TemplateDef", [f"name='{self.name}'"], children

@dataclass(slots=True)
class NamedArg(Node):
    """Argumento nombrado en uso de plantilla: @param=valor"""
    name: str
    value: 'Value'
    loc: Loc
    def _pretty_string_parts(self):
        return "NamedArg", [f"name='{self.name}'"], [self.value]

@dataclass(slots=True)
class TemplateUse(Node):
    """Uso de plantilla: usar NOMBRE(args)"""
    name: str
    args: List[Union['Value', NamedArg]]
    loc: Loc
    def _pretty_string_parts(self):
        return "TemplateUse", [f"name='{self.name}'"], self.args


# === Union Types for Type Hinting ===

Selector = Union[SimpleSelector, CompoundSelector, ComplexSelector]

Value = Union[
    ColorLiteral, Number, Dimension, Percentage, Keyword,
    String, Url, Function, SpaceList, VariableRef
]

AtRule = Union[MediaQuery, VariableDecl, TemplateUse]

ASTNode = Union[
    Stylesheet, RuleSet, SimpleSelector, CompoundSelector, ComplexSelector,
    Declaration, Value, AtRule, Param, TemplateDef, NamedArg
]
