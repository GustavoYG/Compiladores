# cssx/codegen/ast_css_generator.py

from cssx.ast.nodes import *
from cssx.ast.visitor import ASTWalker
from cssx.lexer.dictionaries import DICCIONARIO_CSS

class AstCssGenerator(ASTWalker):
    """
    Generates CSS from an AST.
    """
    def __init__(self):
        self.css = []
        self.indent_level = 0
        self.current_path = []

    def generate(self, ast: Stylesheet) -> str:
        self.visit(ast)
        return '\n'.join(self.css)

    def indent(self):
        return '  ' * self.indent_level

    def visit_Stylesheet(self, node: Stylesheet):
        for child in node.children:
            # Skip template definitions and global declarations like 'titulo_pagina'
            if not isinstance(child, (TemplateDef, VariableDecl)) and \
               not (isinstance(child, Declaration) and child.prop == 'titulo_pagina'):
                self.visit(child)

    def visit_RuleSet(self, node: RuleSet):
        if not node.selectors:
            return

        selector_str = self._render_selectors(node.selectors)
        
        # Handle nested rules
        parent_selector = ' '.join(self.current_path)
        full_selector = f"{parent_selector} {selector_str}".strip() if parent_selector else selector_str
        
        # Group declarations by selector
        declarations = [decl for decl in node.declarations if isinstance(decl, Declaration)]
        
        if declarations:
            self.css.append(f"{self.indent()}{full_selector} {{")
            self.indent_level += 1
            for decl in declarations:
                self.visit(decl)
            self.indent_level -= 1
            self.css.append(f"{self.indent()}}}")
            self.css.append('') # Add a blank line for readability

        # Visit nested rules
        if node.children:
            self.current_path.append(selector_str)
            for child in node.children:
                self.visit(child)
            self.current_path.pop()

    def visit_Declaration(self, node: Declaration):
        # Ignore special properties used for HTML generation
        if node.prop in ('texto', 'contenido', 'enlace', 'titulo_pagina'):
            return

        # Translate property name if in dictionary, otherwise use as is
        prop_name = DICCIONARIO_CSS.get(node.prop, node.prop)
        value_str = self._render_value(node.value)
        
        # Handle properties that need 'px' suffix for numeric values
        if isinstance(node.value, Number) and prop_name in [
            'font-size', 'width', 'height', 'margin', 'padding', 
            'border-radius', 'top', 'left', 'right', 'bottom',
            'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'grid-gap', 'grid-column-gap', 'grid-row-gap'
        ]:
            value_str += 'px'

        self.css.append(f"{self.indent()}{prop_name}: {value_str};")

    def _render_selectors(self, selectors: list) -> str:
        return ', '.join([self._render_selector(s) for s in selectors])

    def _render_selector(self, selector) -> str:
        if isinstance(selector, SimpleSelector):
            if selector.kind == 'type':
                return selector.value
            elif selector.kind == 'class':
                return f".{selector.value}"
            elif selector.kind == 'id':
                return f"#{selector.value}"
            elif selector.kind == 'pseudo':
                return f":{selector.value}"
            elif selector.kind == 'pseudo_elem':
                return f"::{selector.value}"
            else:
                return selector.value
        elif isinstance(selector, CompoundSelector):
            return "".join(self._render_selector(part) for part in selector.parts)
        elif isinstance(selector, ComplexSelector):
            left = self._render_selector(selector.left)
            right = self._render_selector(selector.right)
            if selector.combinator == ' ':
                return f"{left} {right}"
            else:
                return f"{left} {selector.combinator} {right}"
        return ''

    def _render_value(self, value: Value) -> str:
        if isinstance(value, String):
            return f'"{value.text}"'
        elif isinstance(value, ColorLiteral):
            return value.name_or_hex
        elif isinstance(value, Dimension):
            # Format dimension numbers cleanly
            num = int(value.n) if value.n == int(value.n) else value.n
            return f"{num}{value.unit}"
        elif isinstance(value, Number):
            # Format numbers cleanly (e.g., 16 instead of 16.0)
            return str(int(value.n) if value.n == int(value.n) else value.n)
        elif isinstance(value, Percentage):
            num = int(value.n) if value.n == int(value.n) else value.n
            return f"{num}%"
        elif isinstance(value, Keyword):
            return value.name
        elif isinstance(value, VariableRef):
            # This should not happen if the VariableResolver has run
            return f"var(--{value.name.lstrip('@')})"
        elif isinstance(value, Function):
            # Render arguments cleanly
            args = ', '.join(self._render_value(arg) if hasattr(arg, 'to_dict') else str(arg) for arg in value.args)
            return f"{value.name}({args})"
        elif isinstance(value, Url):
            return f'url("{value.path}")'
        elif isinstance(value, SpaceList):
            return ' '.join([self._render_value(item) for item in value.items])
        return ''
