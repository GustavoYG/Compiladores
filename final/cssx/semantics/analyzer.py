# analyzer.py
# Analizador semántico principal que genera diagnósticos

from typing import List, Tuple
import copy
from cssx.ast.nodes import *
from cssx.ast.visitor import ASTWalker
from cssx.semantics.diagnostics import DiagnosticCollector, ErrorCodes, WarningCodes
from cssx.semantics.types import SemanticContext, is_valid_css_identifier
from cssx.semantics.properties import VALID_STANDARD_CSS_PROPERTIES
from cssx.semantics.symbols import ScopeAnalyzer
from cssx.lexer.dictionaries import DICCIONARIO_CSS
from cssx.semantics.templates import collect_templates, expand_templates

class VariableResolver(ASTWalker):
    """
    A visitor that resolves variable references in the AST,
    replacing VariableRef nodes with their corresponding Value nodes.
    """
    def __init__(self, context: SemanticContext):
        self.context = context

    def resolve(self, node: ASTNode) -> ASTNode:
        """
        Starts the resolution process from the given node.
        We deepcopy the node to avoid modifying the original AST, which might be cached.
        """
        node_copy = copy.deepcopy(node)
        self.visit(node_copy)
        return node_copy

    def visit_Declaration(self, node: Declaration):
        if isinstance(node.value, VariableRef):
            resolved_value = self.context.get_variable(node.value.name)
            if resolved_value:
                # Recursively resolve if the variable holds another variable
                if isinstance(resolved_value, VariableRef):
                    node.value = self.visit(resolved_value)
                else:
                    node.value = resolved_value
        elif hasattr(node.value, 'visit'):
            self.visit(node.value)
    
    def visit_VariableRef(self, node: VariableRef):
        # This method is key. It replaces the node itself.
        # This is unconventional for a visitor, so we return the new value.
        resolved_value = self.context.get_variable(node.name)
        if resolved_value:
            # If the resolved value is another variable, resolve it recursively.
            if isinstance(resolved_value, VariableRef):
                return self.visit(resolved_value)
            return resolved_value
        return node # Return the node itself if not found (error already reported)

    def visit_RuleSet(self, node: RuleSet):
        # We need to manually iterate and replace to handle node replacement
        new_declarations = []
        for decl in node.declarations:
            if isinstance(decl, Declaration) and isinstance(decl.value, VariableRef):
                resolved = self.visit(decl.value)
                if resolved:
                    decl.value = resolved
            new_declarations.append(decl)
        node.declarations = new_declarations

        for child in node.children:
            self.visit(child)


class SemanticAnalyzer(ASTWalker):
    """Analizador semántico principal"""
    
    def __init__(self, filename: str = "<unknown>"):
        super().__init__()
        self.diagnostics = DiagnosticCollector()
        self.filename = filename
        self.context = SemanticContext()
        self.scope_analyzer = ScopeAnalyzer()
        self.context.current_file = filename
    
    def analyze(self, ast: Stylesheet) -> Tuple[List, SemanticContext]:
        """Punto de entrada principal para el análisis"""
        tpl_table, tpl_diagnostics = collect_templates(ast)
        self.diagnostics.diagnostics.extend(tpl_diagnostics)
        
        expansion_diagnostics = expand_templates(ast, tpl_table)
        self.diagnostics.diagnostics.extend(expansion_diagnostics)
        
        self.visit(ast)
        
        self._analyze_unused_variables()
        self._analyze_undefined_references()
        
        return self.diagnostics.get_diagnostics(), self.context
    
    def visit_Stylesheet(self, node: Stylesheet) -> None:
        for child in node.children:
            if not isinstance(child, TemplateDef):
                self.visit(child)
    
    def visit_TemplateDef(self, node: TemplateDef) -> None:
        pass
    
    def visit_VariableDecl(self, node: VariableDecl) -> None:
        if hasattr(node.value, '__class__'):
            self.visit(node.value)
        
        # After visiting, the value might be resolved.
        resolved_value = node.value
        if isinstance(node.value, VariableRef):
            val = self.context.get_variable(node.value.name)
            if val:
                resolved_value = val

        self.scope_analyzer.analyze_variable_declaration(node)
        self.context.set_variable(node.name, resolved_value, node.loc)
    
    def visit_RuleSet(self, node: RuleSet) -> None:
        self.scope_analyzer.enter_new_scope()
        for selector in node.selectors:
            self._analyze_selector(selector)
        
        declared_properties = set()
        for declaration in node.declarations:
            if isinstance(declaration, Declaration):
                self._analyze_declaration(declaration, declared_properties)
        
        for child in node.children:
            self.visit(child)
        
        self.scope_analyzer.exit_current_scope()
    
    def visit_Declaration(self, node: Declaration) -> None:
        if hasattr(node.value, '__class__'):
            self.visit(node.value)
    
    def visit_VariableRef(self, node: VariableRef) -> None:
        loc = node.loc if hasattr(node, 'loc') and node.loc else Loc(self.filename, 1, 1, 0)
        self.context.use_variable(node.name, loc)
        self.scope_analyzer.analyze_variable_reference(node, loc)
        
        if not self.context.has_variable(node.name):
            self.diagnostics.error(
                ErrorCodes.UNDEFINED_VARIABLE,
                f"Variable '{node.name}' no está definida.",
                loc.file, loc.line, loc.col,
                doc_url='docs#variables'
            )
    
    def _analyze_declaration(self, declaration: Declaration, declared_properties: set) -> None:
        prop_name = declaration.prop
        
        special_props = {'titulo_pagina', 'texto', 'contenido', 'enlace'}
        if prop_name in special_props:
            self.visit(declaration)
            return

        if prop_name in declared_properties:
            self.diagnostics.warning(
                "W005", # Using custom code for duplicate property
                f"Propiedad '{prop_name}' está duplicada.",
                declaration.loc.file, declaration.loc.line, declaration.loc.col
            )
        declared_properties.add(prop_name)
        
        if prop_name not in DICCIONARIO_CSS and prop_name not in VALID_STANDARD_CSS_PROPERTIES:
            self.diagnostics.error(
                ErrorCodes.INVALID_PROPERTY,
                f"Propiedad '{prop_name}' no es reconocida.",
                declaration.loc.file, declaration.loc.line, declaration.loc.col,
                doc_url='docs#propiedades'
            )
        
        self.visit(declaration)

    def _analyze_selector(self, selector: Selector) -> None:
        if isinstance(selector, SimpleSelector):
            if selector.kind in ['class', 'id'] and not is_valid_css_identifier(selector.value):
                self.diagnostics.error(
                    ErrorCodes.INVALID_VALUE,
                    f"Identificador '{selector.value}' no es válido para {selector.kind}",
                    selector.loc.file, selector.loc.line, selector.loc.col
                )
        elif isinstance(selector, CompoundSelector):
            for part in selector.parts:
                self._analyze_selector(part)
        elif isinstance(selector, ComplexSelector):
            self._analyze_selector(selector.left)
            self._analyze_selector(selector.right)

    def _analyze_unused_variables(self) -> None:
        unused_vars = self.context.get_unused_variables()
        for var_name, loc in unused_vars:
            self.diagnostics.warning(
                WarningCodes.UNUSED_VARIABLE,
                f"Variable '{var_name}' está definida pero no se usa.",
                loc.file, loc.line, loc.col
            )
    
    def _analyze_undefined_references(self) -> None:
        # This is now partially handled in visit_VariableRef, but this catches more cases.
        pass