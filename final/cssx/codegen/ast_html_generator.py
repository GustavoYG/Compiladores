# cssx/codegen/ast_html_generator.py

from cssx.ast.nodes import *
from cssx.ast.visitor import ASTWalker
from cssx.lexer.dictionaries import DICCIONARIO_HTML

class AstHtmlGenerator(ASTWalker):
    """
    Generates HTML from an AST by recursively walking the tree structure.
    """
    def __init__(self):
        self.html_parts = []
        self.indent_level = 0
        self.title = "Generated Page"

    def generate(self, ast: Stylesheet) -> (str, str):
        self.visit(ast)
        body = '\n'.join(self.html_parts)
        return self.title, body

    def indent(self):
        return '  ' * self.indent_level

    def visit_Stylesheet(self, node: Stylesheet):
        # First, find the page title from global declarations
        for child in node.children:
            if isinstance(child, Declaration) and child.prop == 'titulo_pagina':
                if isinstance(child.value, String):
                    self.title = child.value.text
                break
        
        # Then, build the body by visiting only the top-level RuleSet nodes
        for child in node.children:
            if isinstance(child, RuleSet):
                self.visit(child)

    def visit_RuleSet(self, node: RuleSet):
        if not node.selectors:
            return

        # --- 1. Determine Tag and Attributes ---
        selector = node.selectors[0]
        tag, attributes = self._selector_to_tag(selector)

        text_content = ''
        link_href = None

        # --- 2. Find Special Properties for HTML Generation ---
        # These are declarations that directly affect the HTML output for this node
        html_declarations = [d for d in node.declarations if isinstance(d, Declaration)]
        
        for decl in html_declarations:
            if decl.prop in ('texto', 'contenido'):
                if isinstance(decl.value, String):
                    text_content = decl.value.text
                elif isinstance(decl.value, Number):
                    text_content = str(decl.value.n)
            
            if decl.prop == 'enlace':
                if isinstance(decl.value, String):
                    link_href = decl.value.text

        # If an 'enlace' is present, the tag must be 'a'
        if link_href is not None:
            tag = 'a'
            href_attr = f'href="{link_href}"'
            attributes = f'{href_attr} {attributes}'.strip()

        # --- 3. Generate Opening Tag ---
        self.html_parts.append(f"{self.indent()}<{tag}{' ' + attributes if attributes else ''}>")

        # --- 4. Generate Inner Content (Text and Nested Elements) ---
        self.indent_level += 1

        # Add text content if it exists
        if text_content:
            self.html_parts.append(f"{self.indent()}{text_content}")

        # Recursively visit only nested RuleSet children
        for child in node.children:
            if isinstance(child, RuleSet):
                self.visit(child)
        
        self.indent_level -= 1

        # --- 5. Generate Closing Tag ---
        self.html_parts.append(f"{self.indent()}</{tag}>")

    def _selector_to_tag(self, selector: Selector) -> (str, str):
        tag = 'div'
        attrs = []

        # Handles simple selectors like 'p', '.class', '#id'
        if isinstance(selector, SimpleSelector):
            if selector.kind == 'type':
                tag = DICCIONARIO_HTML.get(selector.value, selector.value)
            elif selector.kind == 'class':
                attrs.append(f'class="{selector.value}"')
            elif selector.kind == 'id':
                attrs.append(f'id="{selector.value}"')
        
        # Handles compound selectors like 'div.my-class'
        elif isinstance(selector, CompoundSelector):
            class_list = []
            for part in selector.parts:
                if part.kind == 'type':
                    tag = DICCIONARIO_HTML.get(part.value, part.value)
                elif part.kind == 'class':
                    class_list.append(part.value)
                elif part.kind == 'id':
                    attrs.append(f'id="{part.value}"')
            if class_list:
                attrs.append(f'class="{" ".join(class_list)}"')

        # For complex selectors like 'div > p', we only consider the rightmost part
        # for HTML generation, as it represents the direct element being created.
        elif isinstance(selector, ComplexSelector):
            return self._selector_to_tag(selector.right)

        return tag, ' '.join(attrs)

    def visit_Declaration(self, node: Declaration):
        # This visitor only cares about RuleSets for generating HTML structure.
        # Declarations are handled inside visit_RuleSet.
        pass