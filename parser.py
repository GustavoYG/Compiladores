from cssx.ast.nodes import (
    Stylesheet, RuleSet, Declaration, Loc,
    SimpleSelector, CompoundSelector, ComplexSelector,
    ColorLiteral, Keyword, VariableDecl,
)
import re

def parse(input_text: str, filename: str = "<input>") -> Stylesheet:
    """
    Parser minimal adaptado que soporta variables, anidamiento y selectores con '&'.
    Devuelve un Stylesheet con loc en todos los nodos.
    """
    lines = input_text.splitlines()
    children = []
    line_num = 0
    stack = []
    cur_selectors = []
    cur_decls = []
    cur_children = []
    INDENT = 2  # no usado, pero útil si quieres indentación real

    def parse_selector(sel_str, loc):
        # Muy básico: .clase, #id, tipo, &.algo
        if sel_str.startswith("."):
            return CompoundSelector(parts=(SimpleSelector("class", sel_str[1:], loc),), loc=loc)
        elif sel_str.startswith("#"):
            return CompoundSelector(parts=(SimpleSelector("id", sel_str[1:], loc),), loc=loc)
        elif sel_str.startswith("&"):
            # &.algo => ComplexSelector('&', ' ', .algo)
            left = SimpleSelector("type", "&", loc)
            right = CompoundSelector(parts=(SimpleSelector("class", sel_str[2:], loc),), loc=loc)
            return ComplexSelector(left=left, combinator='', right=right, loc=loc)
        else:
            return CompoundSelector(parts=(SimpleSelector("type", sel_str, loc),), loc=loc)

    def parse_value(val, loc):
        # Muy simple: color, número, keyword
        val = val.strip()
        if re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", val):
            return ColorLiteral(val)
        elif val.isdigit():
            return Keyword(val)
        elif val.startswith('"') and val.endswith('"'):
            return Keyword(val.strip('"'))
        else:
            return Keyword(val)

    i = 0
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        s = line.strip()
        if not s or s.startswith("//"):
            i += 1
            continue
        col = line.find(s) + 1
        loc = Loc(line=line_num, column=col, offset=0)
        if s.startswith("@"):
            # Variable
            m = re.match(r"@(\w+)\s*=\s*(.+)", s)
            if m:
                name, val = m.group(1), m.group(2)
                children.append(VariableDecl(name=name, value=parse_value(val, loc), loc=loc))
        elif s.endswith("{"):
            selector = s[:-1].strip()
            cur_selectors.append(parse_selector(selector, loc))
            # Entrar a bloque
            stack.append((cur_selectors, cur_decls, cur_children))
            cur_selectors, cur_decls, cur_children = [], [], []
        elif s == "}":
            # Salir de bloque
            if not stack:
                raise SyntaxError(f"Unmatched }} at line {line_num}")
            parent_selectors, parent_decls, parent_children = stack.pop()
            ruleset = RuleSet(
                selectors=cur_selectors,
                declarations=cur_decls,
                children=cur_children,
                loc=loc
            )
            cur_selectors, cur_decls, cur_children = parent_selectors, parent_decls, parent_children
            cur_children.append(ruleset)
        elif "=" in s:
            prop, val = map(str.strip, s.split("=", 1))
            cur_decls.append(Declaration(prop=prop, value=parse_value(val, loc), important=False, loc=loc))
        else:
            # Selector sin llaves
            cur_selectors.append(parse_selector(s, loc))
        i += 1

    # Lo que quede en el stack es raíz
    while stack:
        parent_selectors, parent_decls, parent_children = stack.pop()
        ruleset = RuleSet(
            selectors=cur_selectors,
            declarations=cur_decls,
            children=cur_children,
            loc=Loc(line=0, column=0, offset=0)
        )
        cur_selectors, cur_decls, cur_children = parent_selectors, parent_decls, parent_children
        cur_children.append(ruleset)

    sheet = Stylesheet(children=children + cur_children, loc=Loc(line=1, column=1, offset=0))
    return sheet