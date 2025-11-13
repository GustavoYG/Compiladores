from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Literal, Any, Union

@dataclass(slots=True)
class Loc:
    line: int
    column: int
    offset: int

    def __repr__(self):
        return f"(L{self.line}:C{self.column})"

# --- Selectors ---

@dataclass(slots=True)
class SimpleSelector:
    kind: Literal['type', 'class', 'id', 'attr', 'pseudo', 'pseudo_elem']
    value: str
    loc: Loc

    def __repr__(self):
        return f"{self.kind}:{self.value}"

@dataclass(slots=True)
class CompoundSelector:
    parts: Tuple[SimpleSelector, ...]
    loc: Loc

    def __repr__(self):
        return "".join([str(p) for p in self.parts])

@dataclass(slots=True)
class ComplexSelector:
    left: Any  # CompoundSelector or ComplexSelector
    combinator: Literal[' ', '>', '+', '~', '&']
    right: Any  # CompoundSelector or ComplexSelector
    loc: Loc

    def specificity(self) -> Tuple[int, int, int]:
        # id, class/attr/pseudo, type
        def score(sel):
            if isinstance(sel, SimpleSelector):
                if sel.kind == "id":
                    return (1,0,0)
                elif sel.kind in {"class", "attr", "pseudo", "pseudo_elem"}:
                    return (0,1,0)
                elif sel.kind == "type":
                    return (0,0,1)
                else:
                    return (0,0,0)
            elif isinstance(sel, CompoundSelector):
                s = [score(p) for p in sel.parts]
                return tuple(sum(x) for x in zip(*s)) if s else (0,0,0)
            elif isinstance(sel, ComplexSelector):
                l = score(sel.left)
                r = score(sel.right)
                return tuple(sum(x) for x in zip(l, r))
            else:
                return (0,0,0)
        return score(self)
    
    def __repr__(self):
        return f"{self.left}{self.combinator}{self.right}"

# --- Values ---

@dataclass(slots=True, frozen=True)
class ColorLiteral:
    value: str

    def __repr__(self): return self.value

@dataclass(slots=True, frozen=True)
class Number:
    value: float

    def __repr__(self): return str(self.value)

@dataclass(slots=True, frozen=True)
class Dimension:
    value: float
    unit: str

    def __repr__(self): return f"{self.value}{self.unit}"

@dataclass(slots=True, frozen=True)
class Percentage:
    value: float

    def __repr__(self): return f"{self.value}%"

@dataclass(slots=True, frozen=True)
class Keyword:
    value: str

    def __repr__(self): return self.value

@dataclass(slots=True, frozen=True)
class String:
    value: str

    def __repr__(self): return f"\"{self.value}\""

@dataclass(slots=True, frozen=True)
class Url:
    value: str

    def __repr__(self): return f"url({self.value})"

@dataclass(slots=True, frozen=True)
class Function:
    name: str
    args: Tuple[Any, ...]

    def __repr__(self):
        args = ", ".join(map(str, self.args))
        return f"{self.name}({args})"

@dataclass(slots=True, frozen=True)
class SpaceList:
    items: Tuple[Any, ...]

    def __repr__(self):
        return " ".join(map(str, self.items))

@dataclass(slots=True, frozen=True)
class VariableRef:
    name: str

    def __repr__(self):
        return f"@{self.name}"

Value = Union[
    ColorLiteral, Number, Dimension, Percentage, Keyword,
    String, Url, Function, SpaceList, VariableRef,
]

# --- Params for templates ---

@dataclass(slots=True, frozen=True)
class Param:
    name: str
    default: Optional[Value] = None

# --- Declarations ---

@dataclass(slots=True)
class Declaration:
    prop: str
    value: Value
    important: bool
    loc: Loc
    _fp: Optional[int] = field(default=None, compare=False, repr=False)

    def fingerprint(self) -> int:
        if self._fp is not None:
            return self._fp
        h = hash((self.prop, self.value, self.important))
        object.__setattr__(self, "_fp", h)
        return h

    def __repr__(self):
        return f"{self.prop}: {self.value}{' !important' if self.important else ''}"

# --- AST nodes ---

@dataclass(slots=True)
class VariableDecl:
    name: str
    value: Value
    loc: Loc

    def __repr__(self):
        return f"@{self.name} = {self.value}"

@dataclass(slots=True)
class TemplateDef:
    name: str
    params: Tuple[Param, ...]
    body: Tuple[Declaration, ...]
    loc: Loc

@dataclass(slots=True)
class TemplateUse:
    name: str
    args: Tuple[Value, ...]
    loc: Loc

@dataclass(slots=True)
class MediaQuery:
    query: str
    children: List[Any]
    loc: Loc

@dataclass(slots=True)
class RuleSet:
    selectors: List[Any]  # Selector nodes
    declarations: List[Declaration]
    children: List[Any]   # RuleSet|AtRule
    loc: Loc

    def __repr__(self):
        sel = ", ".join(map(str, self.selectors))
        decls = "; ".join(map(str, self.declarations))
        kids = f" ({len(self.children)} hijos)" if self.children else ""
        return f"{sel} {{ {decls} }}{kids}"

@dataclass(slots=True)
class Stylesheet:
    children: List[Any]
    loc: Loc

    def __repr__(self):
        return f"Stylesheet({len(self.children)} reglas)"
