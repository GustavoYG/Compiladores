# templates.py
# Sistema de plantillas CSSX con validación y expansión

import copy
from typing import Dict, List, Set, Union, Optional, Tuple
from cssx.ast.nodes import *
from cssx.ast.visitor import ASTWalker
from cssx.semantics.diagnostics import Diagnostic, ErrorCodes, WarningCodes


class TemplateTable:
    """Tabla de plantillas registradas"""
    
    def __init__(self):
        self.templates: Dict[str, TemplateDef] = {}
    
    def register(self, template: TemplateDef) -> Optional[str]:
        """
        Registra una plantilla. Retorna error si ya existe.
        """
        if template.name in self.templates:
            return f"Plantilla '{template.name}' ya está definida"
        
        self.templates[template.name] = template
        return None
    
    def get(self, name: str) -> Optional[TemplateDef]:
        """Obtiene una plantilla por nombre"""
        return self.templates.get(name)
    
    def exists(self, name: str) -> bool:
        """Verifica si existe una plantilla"""
        return name in self.templates


class TemplateExpander:
    """Expandidor de plantillas con detección de recursión"""
    
    def __init__(self, template_table: TemplateTable):
        self.template_table = template_table
        self.expansion_stack: List[str] = []  # Stack para detectar recursión
        self.max_depth = 50  # Límite de profundidad para evitar recursión infinita
        self.diagnostics: List[Diagnostic] = []
    
    def expand_template_use(self, template_use: TemplateUse, context_loc: Loc) -> List[Declaration]:
        """
        Expande un uso de plantilla retornando las declaraciones resultantes.
        Detecta recursión y valida argumentos.
        """
        # Verificar que la plantilla existe
        template = self.template_table.get(template_use.name)
        if not template:
            self.diagnostics.append(Diagnostic(
                code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                severity="ERROR",
                message=f"Plantilla '{template_use.name}' no está definida",
                file=context_loc.file,
                line=context_loc.line,
                col=context_loc.col,
                doc_url="internal://plantillas"
            ))
            return []
        
        # Detectar recursión
        if template_use.name in self.expansion_stack:
            cycle = " -> ".join(self.expansion_stack + [template_use.name])
            self.diagnostics.append(Diagnostic(
                code=ErrorCodes.TEMPLATE_RECURSION,
                severity="ERROR",
                message=f"Recursión detectada en plantillas: {cycle}",
                file=context_loc.file,
                line=context_loc.line,
                col=context_loc.col,
                doc_url="internal://plantillas"
            ))
            return []
        
        # Verificar límite de profundidad
        if len(self.expansion_stack) >= self.max_depth:
            self.diagnostics.append(Diagnostic(
                code=ErrorCodes.TEMPLATE_RECURSION,
                severity="ERROR",
                message=f"Profundidad máxima de expansión excedida ({self.max_depth})",
                file=context_loc.file,
                line=context_loc.line,
                col=context_loc.col,
                doc_url="internal://plantillas"
            ))
            return []
        
        # Validar y asociar argumentos con parámetros
        param_values = self._bind_arguments(template, template_use, context_loc)
        if param_values is None:
            return []  # Error en binding, ya reportado
        
        # Expandir con stack de recursión
        self.expansion_stack.append(template_use.name)
        try:
            expanded_declarations = self._expand_template_body(template.body, param_values, context_loc)
        finally:
            self.expansion_stack.pop()
        
        return expanded_declarations
    
    def _bind_arguments(self, template: TemplateDef, template_use: TemplateUse, context_loc: Loc) -> Optional[Dict[str, Value]]:
        """
        Asocia argumentos del uso con parámetros de la plantilla.
        Retorna dict {param_name: value} o None si hay error.
        """
        param_values = {}
        
        # Verificar si hay mezcla de argumentos posicionales y nombrados
        has_named = any(isinstance(arg, NamedArg) for arg in template_use.args)
        has_positional = any(not isinstance(arg, NamedArg) for arg in template_use.args)
        
        if has_named and has_positional:
            self.diagnostics.append(Diagnostic(
                code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                severity="ERROR", 
                message="No se pueden mezclar argumentos posicionales y nombrados",
                file=context_loc.file,
                line=context_loc.line,
                col=context_loc.col,
                doc_url="internal://plantillas"
            ))
            return None
        
        if has_named:
            # Argumentos nombrados
            return self._bind_named_arguments(template, template_use, context_loc)
        else:
            # Argumentos posicionales
            return self._bind_positional_arguments(template, template_use, context_loc)
    
    def _bind_positional_arguments(self, template: TemplateDef, template_use: TemplateUse, context_loc: Loc) -> Optional[Dict[str, Value]]:
        """Asocia argumentos posicionales"""
        param_values = {}
        
        # Verificar que no hay demasiados argumentos
        if len(template_use.args) > len(template.params):
            self.diagnostics.append(Diagnostic(
                code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                severity="ERROR",
                message=f"Demasiados argumentos para plantilla '{template.name}'. Esperados: {len(template.params)}, recibidos: {len(template_use.args)}",
                file=context_loc.file,
                line=context_loc.line,
                col=context_loc.col,
                doc_url="internal://plantillas"
            ))
            return None
        
        # Asignar argumentos posicionales
        for i, arg in enumerate(template_use.args):
            param = template.params[i]
            param_values[param.name] = arg
        
        # Asignar valores por defecto para parámetros restantes
        for i in range(len(template_use.args), len(template.params)):
            param = template.params[i]
            if param.default_value is None:
                self.diagnostics.append(Diagnostic(
                    code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                    severity="ERROR",
                    message=f"Parámetro '{param.name}' no tiene valor por defecto y no se proporcionó argumento",
                    file=context_loc.file,
                    line=context_loc.line,
                    col=context_loc.col,
                    doc_url="internal://plantillas"
                ))
                return None
            param_values[param.name] = param.default_value
        
        return param_values
    
    def _bind_named_arguments(self, template: TemplateDef, template_use: TemplateUse, context_loc: Loc) -> Optional[Dict[str, Value]]:
        """Asocia argumentos nombrados"""
        param_values = {}
        param_names = {p.name for p in template.params}
        provided_names = set()
        
        # Procesar argumentos nombrados
        for arg in template_use.args:
            if isinstance(arg, NamedArg):
                if arg.name not in param_names:
                    self.diagnostics.append(Diagnostic(
                        code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                        severity="ERROR",
                        message=f"Parámetro '{arg.name}' no existe en plantilla '{template.name}'",
                        file=context_loc.file,
                        line=context_loc.line,
                        col=context_loc.col,
                        doc_url="internal://plantillas"
                    ))
                    return None
                
                if arg.name in provided_names:
                    self.diagnostics.append(Diagnostic(
                        code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                        severity="ERROR",
                        message=f"Parámetro '{arg.name}' especificado múltiples veces",
                        file=context_loc.file,
                        line=context_loc.line,
                        col=context_loc.col,
                        doc_url="internal://plantillas"
                    ))
                    return None
                
                param_values[arg.name] = arg.value
                provided_names.add(arg.name)
        
        # Asignar valores por defecto para parámetros no proporcionados
        for param in template.params:
            if param.name not in provided_names:
                if param.default_value is None:
                    self.diagnostics.append(Diagnostic(
                        code=ErrorCodes.TEMPLATE_INVOCATION_ERROR,
                        severity="ERROR",
                        message=f"Parámetro requerido '{param.name}' no proporcionado",
                        file=context_loc.file,
                        line=context_loc.line,
                        col=context_loc.col,
                        doc_url="internal://plantillas"
                    ))
                    return None
                param_values[param.name] = param.default_value
        
        return param_values
    
    def _expand_template_body(self, body: List[Declaration], param_values: Dict[str, Value], context_loc: Loc) -> List[Declaration]:
        """
        Expande el cuerpo de una plantilla sustituyendo parámetros por valores.
        """
        expanded_declarations = []
        
        for decl in body:
            # Clonar la declaración para no modificar el original
            new_decl = copy.deepcopy(decl)
            
            # Sustituir referencias a parámetros en el valor
            new_decl.value = self._substitute_parameters(new_decl.value, param_values)
            
            # Mantener ubicación original pero añadir contexto del uso
            if new_decl.loc:
                new_decl.loc.file = context_loc.file
            
            expanded_declarations.append(new_decl)
        
        return expanded_declarations
    
    def _substitute_parameters(self, value: Value, param_values: Dict[str, Value]) -> Value:
        """
        Sustituye referencias a parámetros (@param) en un valor por los valores correspondientes.
        """
        if isinstance(value, VariableRef):
            if value.name in param_values:
                # Sustituir parámetro por su valor
                return copy.deepcopy(param_values[value.name])
            else:
                # Mantener referencia a variable global
                return value
        elif isinstance(value, SpaceList):
            # Sustituir en listas de valores
            new_items = []
            for item in value.items:
                new_items.append(self._substitute_parameters(item, param_values))
            return SpaceList(items=tuple(new_items))
        elif isinstance(value, Function):
            # Sustituir en argumentos de funciones
            new_args = []
            for arg in value.args:
                new_args.append(self._substitute_parameters(arg, param_values))
            return Function(name=value.name, args=new_args, loc=value.loc)
        else:
            # Valores literales no necesitan sustitución
            return value


def collect_templates(ast: Stylesheet) -> Tuple[TemplateTable, List[Diagnostic]]:
    """
    Recorre Stylesheet.children, registra TemplateDef por nombre.
    Si nombre duplicado → E040 con loc del duplicado.
    Retorna (tabla_plantillas, diagnostics).
    """
    template_table = TemplateTable()
    diagnostics = []
    
    for child in ast.children:
        if isinstance(child, TemplateDef):
            error = template_table.register(child)
            if error:
                diagnostics.append(Diagnostic(
                    code=ErrorCodes.TEMPLATE_DUPLICATE,
                    severity="ERROR",
                    message=error,
                    file=child.loc.file,
                    line=child.loc.line,
                    col=child.loc.col,
                    doc_url="internal://plantillas"
                ))
    
    return template_table, diagnostics


def expand_templates(ast: Stylesheet, template_table: TemplateTable) -> List[Diagnostic]:
    """
    Recorre todos los RuleSet y, dentro de declarations, reemplaza cada TemplateUse
    por las Declaration resultantes de la expansión (in-place).
    - Vincula args→params (defaults, posicionales o nombrados).
    - Sustituye referencias a parámetros dentro del cuerpo: VariableRef('@p') → Value del argumento.
    - Permite que queden VariableRef de variables globales (se resolverán después).
    - Detecta recursión/ciclo (E041). Proteger con stack y límite de profundidad.
    - Aridad/param desconocido → E042.
    Retorna lista de Diagnostic.
    """
    expander = TemplateExpander(template_table)
    
    def expand_in_ruleset(ruleset: RuleSet):
        """Expande plantillas en un ruleset recursivamente"""
        new_declarations = []
        
        for item in ruleset.declarations:
            if isinstance(item, TemplateUse):
                # Expandir uso de plantilla
                expanded_decls = expander.expand_template_use(item, item.loc)
                new_declarations.extend(expanded_decls)
            else:
                # Mantener declaración normal
                new_declarations.append(item)
        
        # Reemplazar declaraciones con versión expandida
        ruleset.declarations = new_declarations
        
        # Expandir recursivamente en rulesets anidados
        for child in ruleset.children:
            if isinstance(child, RuleSet):
                expand_in_ruleset(child)
    
    # Expandir en todos los rulesets del stylesheet
    for child in ast.children:
        if isinstance(child, RuleSet):
            expand_in_ruleset(child)
    
    return expander.diagnostics
