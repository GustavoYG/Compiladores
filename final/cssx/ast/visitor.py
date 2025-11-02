# visitor.py
# Patrón Visitor para recorrer y transformar el AST

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic
from cssx.ast.nodes import *

T = TypeVar('T')


class ASTVisitor(ABC, Generic[T]):
    """Clase base abstracta para implementar visitantes del AST"""
    
    def visit(self, node: ASTNode) -> T:
        """Método principal para visitar un nodo"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> T:
        """Método genérico para nodos no implementados específicamente"""
        # Si es un string, devolverlo tal como está
        if isinstance(node, str):
            return node
        raise NotImplementedError(f"No hay método visit_{type(node).__name__} implementado")


class ASTTransformer(ASTVisitor[ASTNode]):
    """Visitante que transforma el AST, devolviendo un nuevo AST"""
    
    def visit_Stylesheet(self, node: Stylesheet) -> Stylesheet:
        """Visita un nodo Stylesheet"""
        new_children = [self.visit(child) for child in node.children]
        return Stylesheet(children=new_children, loc=node.loc)
    
    def visit_RuleSet(self, node: RuleSet) -> RuleSet:
        """Visita un nodo RuleSet"""
        new_selectors = [self.visit(sel) for sel in node.selectors]
        new_declarations = [self.visit(decl) for decl in node.declarations]
        new_children = [self.visit(child) for child in node.children]
        return RuleSet(
            selectors=new_selectors,
            declarations=new_declarations, 
            children=new_children,
            loc=node.loc
        )
    
    def visit_SimpleSelector(self, node: SimpleSelector) -> SimpleSelector:
        """Visita un nodo SimpleSelector"""
        return SimpleSelector(kind=node.kind, value=node.value, loc=node.loc)
    
    def visit_CompoundSelector(self, node: CompoundSelector) -> CompoundSelector:
        """Visita un nodo CompoundSelector"""
        new_parts = tuple(self.visit(part) for part in node.parts)
        return CompoundSelector(parts=new_parts, loc=node.loc)
    
    def visit_ComplexSelector(self, node: ComplexSelector) -> ComplexSelector:
        """Visita un nodo ComplexSelector"""
        new_left = self.visit(node.left)
        new_right = self.visit(node.right)
        return ComplexSelector(
            left=new_left,
            combinator=node.combinator,
            right=new_right,
            loc=node.loc
        )
    
    def visit_Declaration(self, node: Declaration) -> Declaration:
        """Visita un nodo Declaration"""
        new_value = self.visit(node.value) if hasattr(node.value, '__class__') else node.value
        return Declaration(
            prop=node.prop,
            value=new_value,
            important=node.important,
            loc=node.loc,
            fp=node.fp
        )
    
    # === VALORES ===
    
    def visit_ColorLiteral(self, node: ColorLiteral) -> ColorLiteral:
        """Visita un nodo ColorLiteral"""
        return ColorLiteral(name_or_hex=node.name_or_hex)
    
    def visit_Number(self, node: Number) -> Number:
        """Visita un nodo Number"""
        return Number(n=node.n)
    
    def visit_Dimension(self, node: Dimension) -> Dimension:
        """Visita un nodo Dimension"""
        return Dimension(n=node.n, unit=node.unit)
    
    def visit_Percentage(self, node: Percentage) -> Percentage:
        """Visita un nodo Percentage"""
        return Percentage(n=node.n)
    
    def visit_Keyword(self, node: Keyword) -> Keyword:
        """Visita un nodo Keyword"""
        return Keyword(name=node.name)
    
    def visit_String(self, node: String) -> String:
        """Visita un nodo String"""
        return String(text=node.text)
    
    def visit_Url(self, node: Url) -> Url:
        """Visita un nodo Url"""
        return Url(path=node.path)
    
    def visit_Function(self, node: Function) -> Function:
        """Visita un nodo Function"""
        new_args = tuple(self.visit(arg) if hasattr(arg, '__class__') else arg for arg in node.args)
        return Function(name=node.name, args=new_args)
    
    def visit_SpaceList(self, node: SpaceList) -> SpaceList:
        """Visita un nodo SpaceList"""
        new_items = tuple(self.visit(item) if hasattr(item, '__class__') else item for item in node.items)
        return SpaceList(items=new_items)
    
    def visit_VariableRef(self, node: VariableRef) -> VariableRef:
        """Visita un nodo VariableRef"""
        return VariableRef(name=node.name)
    
    # === AT-RULES Y PLANTILLAS ===
    
    def visit_MediaQuery(self, node: MediaQuery) -> MediaQuery:
        """Visita un nodo MediaQuery"""
        new_children = [self.visit(child) for child in node.children]
        return MediaQuery(query=node.query, children=new_children, loc=node.loc)
    
    def visit_VariableDecl(self, node: VariableDecl) -> VariableDecl:
        """Visita un nodo VariableDecl"""
        new_value = self.visit(node.value) if hasattr(node.value, '__class__') else node.value
        return VariableDecl(name=node.name, value=new_value, loc=node.loc)
    
    def visit_Param(self, node: Param) -> Param:
        """Visita un nodo Param"""
        new_default = self.visit(node.default_value) if node.default_value and hasattr(node.default_value, '__class__') else node.default_value
        return Param(name=node.name, default_value=new_default, loc=node.loc)
    
    def visit_TemplateDef(self, node: TemplateDef) -> TemplateDef:
        """Visita un nodo TemplateDef"""
        new_params = tuple(self.visit(param) for param in node.params)
        new_body = tuple(self.visit(decl) for decl in node.body)
        return TemplateDef(name=node.name, params=new_params, body=new_body, loc=node.loc)
    
    def visit_TemplateUse(self, node: TemplateUse) -> TemplateUse:
        """Visita un nodo TemplateUse"""
        new_args = tuple(self.visit(arg) if hasattr(arg, '__class__') else arg for arg in node.args)
        return TemplateUse(name=node.name, args=new_args, loc=node.loc)


class ASTWalker(ASTVisitor[None]):
    """Visitante que recorre el AST sin transformarlo (para análisis, depuración, etc.)"""
    
    def visit_Stylesheet(self, node: Stylesheet) -> None:
        """Visita un nodo Stylesheet"""
        for child in node.children:
            self.visit(child)
    
    def visit_RuleSet(self, node: RuleSet) -> None:
        """Visita un nodo RuleSet"""
        for selector in node.selectors:
            self.visit(selector)
        for declaration in node.declarations:
            self.visit(declaration)
        for child in node.children:
            self.visit(child)
    
    def visit_SimpleSelector(self, node: SimpleSelector) -> None:
        """Visita un nodo SimpleSelector"""
        pass
    
    def visit_CompoundSelector(self, node: CompoundSelector) -> None:
        """Visita un nodo CompoundSelector"""
        for part in node.parts:
            self.visit(part)
    
    def visit_ComplexSelector(self, node: ComplexSelector) -> None:
        """Visita un nodo ComplexSelector"""
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_Declaration(self, node: Declaration) -> None:
        """Visita un nodo Declaration"""
        if hasattr(node.value, '__class__'):
            self.visit(node.value)
    
    # === VALORES ===
    
    def visit_ColorLiteral(self, node: ColorLiteral) -> None:
        """Visita un nodo ColorLiteral"""
        pass
    
    def visit_Number(self, node: Number) -> None:
        """Visita un nodo Number"""
        pass
    
    def visit_Dimension(self, node: Dimension) -> None:
        """Visita un nodo Dimension"""
        pass
    
    def visit_Percentage(self, node: Percentage) -> None:
        """Visita un nodo Percentage"""
        pass
    
    def visit_Keyword(self, node: Keyword) -> None:
        """Visita un nodo Keyword"""
        pass
    
    def visit_String(self, node: String) -> None:
        """Visita un nodo String"""
        pass
    
    def visit_Url(self, node: Url) -> None:
        """Visita un nodo Url"""
        pass
    
    def visit_Function(self, node: Function) -> None:
        """Visita un nodo Function"""
        for arg in node.args:
            if hasattr(arg, '__class__'):
                self.visit(arg)
    
    def visit_SpaceList(self, node: SpaceList) -> None:
        """Visita un nodo SpaceList"""
        for item in node.items:
            if hasattr(item, '__class__'):
                self.visit(item)
    
    def visit_VariableRef(self, node: VariableRef) -> None:
        """Visita un nodo VariableRef"""
        pass
    
    # === AT-RULES Y PLANTILLAS ===
    
    def visit_MediaQuery(self, node: MediaQuery) -> None:
        """Visita un nodo MediaQuery"""
        for child in node.children:
            self.visit(child)
    
    def visit_VariableDecl(self, node: VariableDecl) -> None:
        """Visita un nodo VariableDecl"""
        if hasattr(node.value, '__class__'):
            self.visit(node.value)
    
    def visit_Param(self, node: Param) -> None:
        """Visita un nodo Param"""
        if node.default_value and hasattr(node.default_value, '__class__'):
            self.visit(node.default_value)
    
    def visit_TemplateDef(self, node: TemplateDef) -> None:
        """Visita un nodo TemplateDef"""
        for param in node.params:
            self.visit(param)
        for decl in node.body:
            self.visit(decl)
    
    def visit_TemplateUse(self, node: TemplateUse) -> None:
        """Visita un nodo TemplateUse"""
        for arg in node.args:
            if hasattr(arg, '__class__'):
                self.visit(arg)


class ASTPrinter(ASTWalker):
    """Visitante que imprime la estructura del AST para depuración"""
    
    def __init__(self):
        self.indent_level = 0
    
    def _print(self, text: str):
        """Imprime con indentación"""
        print("  " * self.indent_level + text)
    
    def _with_indent(self, func, *args, **kwargs):
        """Ejecuta una función con indentación incrementada"""
        self.indent_level += 1
        try:
            return func(*args, **kwargs)
        finally:
            self.indent_level -= 1
    
    def visit_Stylesheet(self, node: Stylesheet) -> None:
        """Imprime un nodo Stylesheet"""
        self._print(f"Stylesheet (loc: {node.loc.line}:{node.loc.col})")
        self._with_indent(super().visit_Stylesheet, node)
    
    def visit_RuleSet(self, node: RuleSet) -> None:
        """Imprime un nodo RuleSet"""
        self._print(f"RuleSet (loc: {node.loc.line}:{node.loc.col})")
        self._with_indent(super().visit_RuleSet, node)
    
    def visit_SimpleSelector(self, node: SimpleSelector) -> None:
        """Imprime un nodo SimpleSelector"""
        self._print(f"SimpleSelector({node.kind}: '{node.value}')")
    
    def visit_Declaration(self, node: Declaration) -> None:
        """Imprime un nodo Declaration"""
        importance = " !important" if node.important else ""
        self._print(f"Declaration({node.prop}: {type(node.value).__name__}{importance})")
        self._with_indent(super().visit_Declaration, node)
    
    def visit_ColorLiteral(self, node: ColorLiteral) -> None:
        """Imprime un nodo ColorLiteral"""
        self._print(f"ColorLiteral('{node.name_or_hex}')")
    
    def visit_Number(self, node: Number) -> None:
        """Imprime un nodo Number"""
        self._print(f"Number({node.n})")
    
    def visit_Dimension(self, node: Dimension) -> None:
        """Imprime un nodo Dimension"""
        self._print(f"Dimension({node.n}{node.unit})")
    
    def visit_Keyword(self, node: Keyword) -> None:
        """Imprime un nodo Keyword"""
        self._print(f"Keyword('{node.name}')")
    
    def visit_String(self, node: String) -> None:
        """Imprime un nodo String"""
        self._print(f"String('{node.text}')")

    def visit_str(self, node: str) -> None:
        """Imprime un string simple"""
        self._print(f"str('{node}')")

    def visit_VariableRef(self, node: VariableRef) -> None:
        """Imprime un nodo VariableRef"""
        self._print(f"VariableRef('{node.name}')")
    
    def visit_TemplateDef(self, node) -> None:
        """Imprime un nodo TemplateDef"""
        self._print(f"TemplateDef('{node.name}')")
        self._with_indent(self._visit_template_children, node)
    
    def _visit_template_children(self, node):
        """Helper para visitar hijos de template con indentación"""
        for param in node.params:
            self.visit(param)
        for decl in node.body:
            self.visit(decl)
    
    def visit_TemplateUse(self, node) -> None:
        """Imprime un nodo TemplateUse"""
        self._print(f"TemplateUse('{node.name}')")
        self._with_indent(self._visit_use_args, node)
    
    def _visit_use_args(self, node):
        """Helper para visitar argumentos de template use"""
        for arg in node.args:
            self.visit(arg)
    
    def visit_Param(self, node) -> None:
        """Imprime un nodo Param"""
        self._print(f"Param('{node.name}')")
        if node.default_value:
            self._with_indent(self.visit, node.default_value)
    
    def visit_NamedArg(self, node) -> None:
        """Imprime un nodo NamedArg"""
        self._print(f"NamedArg('{node.name}')")
        self._with_indent(self.visit, node.value)
