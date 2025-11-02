# analyzer.py
# Analizador semántico principal que genera diagnósticos

from typing import List
from cssx.ast.nodes import *
from cssx.ast.visitor import ASTWalker
from cssx.semantics.diagnostics import DiagnosticCollector, ErrorCodes, WarningCodes
from cssx.semantics.types import (
    get_value_type, CSSValueType, is_valid_color, is_valid_length_unit,
    is_valid_css_identifier, validate_selector, SemanticContext
)
from cssx.semantics.properties import (
    VALID_CSS_PROPERTIES, DEPRECATED_PROPERTIES, get_default_value, get_valid_values
)
from cssx.semantics.symbols import ScopeAnalyzer
from cssx.lexer.dictionaries import DICCIONARIO_CSS
from cssx.semantics.templates import collect_templates, expand_templates

# Funciones dummy para reemplazar las de documentación eliminadas
def obtener_propiedad_cssx(prop_name):
    """Dummy function - documentación eliminada"""
    return None

def obtener_url_documentacion(prop_name):
    """Dummy function - documentación eliminada"""
    return None


class SemanticAnalyzer(ASTWalker):
    """Analizador semántico principal"""
    
    def __init__(self, filename: str = "<unknown>"):
        super().__init__()
        self.diagnostics = DiagnosticCollector()
        self.filename = filename
        self.context = SemanticContext()
        self.scope_analyzer = ScopeAnalyzer()
        
        # Configurar contexto
        self.context.current_file = filename
    
    def analyze(self, ast: Stylesheet) -> List:
        """Punto de entrada principal para el análisis"""
        # 1. Recolectar y expandir plantillas (antes de la validación)
        tpl_table, tpl_diagnostics = collect_templates(ast)
        for diag in tpl_diagnostics:
            self.diagnostics.diagnostics.append(diag)
        
        expansion_diagnostics = expand_templates(ast, tpl_table)
        for diag in expansion_diagnostics:
            self.diagnostics.diagnostics.append(diag)
        
        # 2. Análisis semántico normal (sobre AST ya expandido)
        self.visit(ast)
        
        # 3. Análisis post-procesamiento
        self._analyze_unused_variables()
        self._analyze_undefined_references()
        
        return self.diagnostics.get_diagnostics()
    
    def visit_Stylesheet(self, node: Stylesheet) -> None:
        """Analiza el nodo raíz del stylesheet"""
        # Visitar solo los elementos que no sean TemplateDef
        # Las plantillas ya fueron procesadas y expandidas
        for child in node.children:
            if not isinstance(child, TemplateDef):
                self.visit(child)
    
    def visit_TemplateDef(self, node: TemplateDef) -> None:
        """Omite análisis de definiciones de plantillas (ya fueron expandidas)"""
        pass
    
    def visit_VariableDecl(self, node: VariableDecl) -> None:
        """Analiza declaración de variable"""
        # Verificar nombre válido de variable
        if not node.name.startswith('@'):
            self.diagnostics.error(
                ErrorCodes.INVALID_VARIABLE,
                f"El nombre de variable '{node.name}' debe empezar con '@'",
                node.loc.file, node.loc.line, node.loc.col
            )
            return
        
        # Verificar identificador válido
        var_name = node.name[1:]  # Quitar @
        if not is_valid_css_identifier(var_name):
            self.diagnostics.error(
                ErrorCodes.INVALID_VARIABLE,
                f"El nombre de variable '{var_name}' no es un identificador CSS válido",
                node.loc.file, node.loc.line, node.loc.col
            )
            return
        
        # Registrar en tabla de símbolos
        self.scope_analyzer.analyze_variable_declaration(node)
        self.context.set_variable(node.name, node.value, node.loc)
        
        # Analizar el valor de la variable
        if hasattr(node.value, '__class__'):
            self.visit(node.value)
    
    def visit_RuleSet(self, node: RuleSet) -> None:
        """Analiza un conjunto de reglas"""
        # Entrar a nuevo scope
        self.scope_analyzer.enter_new_scope()
        
        # Analizar selectores
        for selector in node.selectors:
            self._analyze_selector(selector)
        
        # Analizar declaraciones
        declared_properties = set()
        for declaration in node.declarations:
            self._analyze_declaration(declaration, declared_properties)
        
        # Analizar hijos (reglas anidadas)
        for child in node.children:
            self.visit(child)
        
        # Salir del scope
        self.scope_analyzer.exit_current_scope()
    
    def visit_Declaration(self, node: Declaration) -> None:
        """Analiza una declaración CSS"""
        # Si es una declaración especial (titulo_pagina, texto, contenido), skip análisis CSS
        if node.prop in ['titulo_pagina', 'texto', 'contenido']:
            if hasattr(node.value, '__class__'):
                self.visit(node.value)
            return
        
        # Analizar valor
        if hasattr(node.value, '__class__'):
            self.visit(node.value)
    
    def visit_VariableRef(self, node: VariableRef) -> None:
        """Analiza referencia a variable"""
        # Usar la ubicación del nodo si está disponible, sino usar ubicación por defecto
        loc = node.loc if hasattr(node, 'loc') and node.loc else Loc(self.filename, 1, 1, 0)
        
        # Marcar variable como usada en el contexto semántico
        self.context.use_variable(node.name, loc)
        
        # También marcar en el scope analyzer
        self.scope_analyzer.analyze_variable_reference(node, loc)
        
        # Verificar que la variable esté definida
        if not self.context.has_variable(node.name):
            self.diagnostics.error(
                ErrorCodes.UNDEFINED_VARIABLE,
                f"Variable '{node.name}' no está definida",
                loc.file, loc.line, loc.col
            )
    
    def visit_ColorLiteral(self, node: ColorLiteral) -> None:
        """Analiza literal de color"""
        if not is_valid_color(node.name_or_hex):
            self.diagnostics.warning(
                WarningCodes.SUSPICIOUS_VALUE,
                f"Color '{node.name_or_hex}' puede no ser válido",
                self.filename, 0, 0
            )
    
    def visit_Dimension(self, node: Dimension) -> None:
        """Analiza dimensión (número + unidad)"""
        if not is_valid_length_unit(node.unit):
            self.diagnostics.error(
                ErrorCodes.INVALID_VALUE,
                f"Unidad '{node.unit}' no es válida",
                self.filename, 0, 0
            )
    
    def visit_Number(self, node: Number) -> None:
        """Analiza número"""
        # Verificar valores sospechosos
        if node.n < 0:
            # Algunos contextos donde números negativos son problemáticos
            self.diagnostics.warning(
                WarningCodes.SUSPICIOUS_VALUE,
                f"Valor negativo {node.n} puede causar problemas",
                self.filename, 0, 0
            )
    
    def _analyze_selector(self, selector: Selector) -> None:
        """Analiza un selector CSS"""
        if isinstance(selector, SimpleSelector):
            self._analyze_simple_selector(selector)
        elif isinstance(selector, CompoundSelector):
            for part in selector.parts:
                self._analyze_simple_selector(part)
        elif isinstance(selector, ComplexSelector):
            self._analyze_selector(selector.left)
            self._analyze_selector(selector.right)
    
    def _analyze_simple_selector(self, selector: SimpleSelector) -> None:
        """Analiza un selector simple"""
        # Verificar identificador válido para clases e IDs
        if selector.kind in ['class', 'id']:
            if not is_valid_css_identifier(selector.value):
                self.diagnostics.error(
                    ErrorCodes.INVALID_VALUE,
                    f"Identificador '{selector.value}' no es válido para {selector.kind}",
                    selector.loc.file, selector.loc.line, selector.loc.col
                )
        
        # Verificar elementos HTML válidos
        if selector.kind == 'type':
            # Elementos HTML comunes - podrías expandir esta lista
            html_elements = {
                'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'body', 'html', 'head', 'title', 'meta', 'link', 'script',
                'header', 'footer', 'nav', 'section', 'article', 'aside',
                'main', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
                'form', 'input', 'button', 'select', 'option', 'textarea',
                'a', 'img', 'video', 'audio', 'canvas'
            }
            
            if selector.value.lower() not in html_elements:
                self.diagnostics.warning(
                    WarningCodes.UNKNOWN_PROPERTY,
                    f"Elemento HTML '{selector.value}' no es estándar",
                    selector.loc.file, selector.loc.line, selector.loc.col
                )
    
    def _analyze_declaration(self, declaration: Declaration, declared_properties: set) -> None:
        """Analiza una declaración CSS"""
        prop_name = declaration.prop
        
        # Verificar propiedades duplicadas
        if prop_name in declared_properties:
            self.diagnostics.warning(
                WarningCodes.SUSPICIOUS_VALUE,
                f"Propiedad '{prop_name}' está duplicada",
                declaration.loc.file, declaration.loc.line, declaration.loc.col
            )
        declared_properties.add(prop_name)
        
        # Verificar si la propiedad CSSX es conocida
        propiedad_cssx = obtener_propiedad_cssx(prop_name)
        
        if not propiedad_cssx:
            # No es una propiedad CSSX conocida
            self.diagnostics.error(
                ErrorCodes.INVALID_PROPERTY,
                f"Propiedad CSSX '{prop_name}' no es conocida. Consulta la documentación para ver propiedades disponibles.",
                declaration.loc.file, declaration.loc.line, declaration.loc.col,
                doc_url=obtener_url_documentacion("propiedades")
            )
        else:
            # Analizar valor vs propiedad CSSX conocida
            self._analyze_property_value_cssx(declaration, propiedad_cssx)
            
            # Verificar si está deprecada
            if propiedad_cssx.deprecada:
                self.diagnostics.warning(
                    WarningCodes.DEPRECATED_PROPERTY,
                    f"Propiedad CSSX '{prop_name}' está deprecada: {propiedad_cssx.descripcion}",
                    declaration.loc.file, declaration.loc.line, declaration.loc.col,
                    doc_url=obtener_url_documentacion(prop_name)
                )
        
        # Analizar el valor
        self.visit(declaration)
    
    def _analyze_property_value_cssx(self, declaration: Declaration, propiedad_cssx) -> None:
        """Analiza el valor de una propiedad CSSX específica"""
        value = declaration.value
        value_type = get_value_type(value)
        
        # Variables siempre son válidas - se resolverán en tiempo de compilación
        if value_type == CSSValueType.VARIABLE:
            return
        
        # Verificar si el tipo de valor es aceptado por la propiedad CSSX
        if not propiedad_cssx.acepta_tipo(value_type):
            tipos_aceptados = ", ".join([t.value for t in propiedad_cssx.valores_aceptados])
            self.diagnostics.error(
                ErrorCodes.INVALID_VALUE,
                f"Propiedad CSSX '{declaration.prop}' no acepta valores de tipo '{value_type.value}'. Tipos válidos: {tipos_aceptados}",
                declaration.loc.file, declaration.loc.line, declaration.loc.col,
                doc_url=obtener_url_documentacion(declaration.prop)
            )
            return
        
        # Verificar palabras clave específicas
        if isinstance(value, Keyword):
            if not propiedad_cssx.acepta_palabra_clave(value.name):
                palabras_validas = ", ".join(propiedad_cssx.palabras_clave)
                self.diagnostics.error(
                    ErrorCodes.INVALID_VALUE,
                    f"Palabra clave '{value.name}' no es válida para la propiedad CSSX '{declaration.prop}'. Palabras válidas: {palabras_validas}",
                    declaration.loc.file, declaration.loc.line, declaration.loc.col,
                    doc_url=obtener_url_documentacion(declaration.prop)
                )
        
        # Sugerencias específicas para propiedades CSSX que manejan unidades automáticamente
        if value_type == CSSValueType.NUMBER and declaration.prop in ['tamano', 'relleno', 'margen', 'redondeado', 'ancho', 'alto']:
            # Estas propiedades automáticamente añaden 'px', así que los números sin unidades son válidos
            # No generar advertencia
            pass
        elif value_type == CSSValueType.NUMBER and declaration.prop not in ['opacidad', 'peso']:
            # Para otras propiedades que no manejan unidades automáticamente, sugerir unidades
            self.diagnostics.warning(
                WarningCodes.SUSPICIOUS_VALUE,
                f"Considera especificar unidades para '{declaration.prop}' (px, em, %, etc.)",
                declaration.loc.file, declaration.loc.line, declaration.loc.col,
                doc_url=obtener_url_documentacion(declaration.prop)
            )
    
    def _analyze_property_value(self, declaration: Declaration, prop_info) -> None:
        """Analiza el valor de una propiedad CSS específica"""
        value = declaration.value
        value_type = get_value_type(value)
        
        # Variables siempre son válidas - se resolverán en tiempo de compilación
        if value_type == CSSValueType.VARIABLE:
            return
        
        # Los números sin unidades son válidos para algunas propiedades específicas
        if value_type == CSSValueType.NUMBER:
            # Propiedades CSS que aceptan números sin unidades
            css_number_accepting_props = {
                'opacity', 'z-index', 'font-weight', 'line-height', 
                'flex-grow', 'flex-shrink', 'order'
            }
            
            # Propiedades CSSX que se traducen a CSS y normalmente necesitan unidades
            # pero en CSSX se asume 'px' automáticamente
            cssx_auto_unit_props = {
                'tamano', 'relleno', 'margen', 'redondeado', 'ancho', 'alto'
            }
            
            # Obtener la propiedad CSS equivalente
            css_prop_name = DICCIONARIO_CSS.get(declaration.prop, declaration.prop)
            
            # Si es una propiedad CSSX que automáticamente añade unidades, no avisar
            if declaration.prop in cssx_auto_unit_props:
                return
            
            # Si la propiedad CSS acepta números sin unidades, no avisar
            if css_prop_name in css_number_accepting_props:
                return
            
            # Para otras propiedades, sugerir unidades
            self.diagnostics.warning(
                WarningCodes.SUSPICIOUS_VALUE,
                f"Número sin unidades para '{declaration.prop}' - considera agregar unidades (px, em, etc.)",
                declaration.loc.file, declaration.loc.line, declaration.loc.col,
                doc_url=prop_info.doc_url
            )
            return
        
        # Verificar si el tipo de valor es aceptado por la propiedad
        if not prop_info.accepts_type(value_type):
            self.diagnostics.error(
                ErrorCodes.INVALID_VALUE,
                f"Propiedad '{declaration.prop}' no acepta valores de tipo {value_type.value}",
                declaration.loc.file, declaration.loc.line, declaration.loc.col,
                doc_url=prop_info.doc_url
            )
        
        # Verificar palabras clave específicas
        if isinstance(value, Keyword):
            if not prop_info.accepts_keyword(value.name):
                self.diagnostics.error(
                    ErrorCodes.INVALID_VALUE,
                    f"Palabra clave '{value.name}' no es válida para la propiedad '{declaration.prop}'",
                    declaration.loc.file, declaration.loc.line, declaration.loc.col,
                    doc_url=prop_info.doc_url
                )
    
    def _analyze_unused_variables(self) -> None:
        """Analiza variables no utilizadas"""
        unused_vars = self.context.get_unused_variables()
        for var_name, loc in unused_vars:
            self.diagnostics.warning(
                WarningCodes.UNUSED_VARIABLE,
                f"Variable '{var_name}' está definida pero no se usa",
                loc.file, loc.line, loc.col
            )
    
    def _analyze_undefined_references(self) -> None:
        """Analiza referencias a variables no definidas"""
        undefined_refs, unused_defs = self.scope_analyzer.get_analysis_results()
        
        for var_name, loc in undefined_refs:
            self.diagnostics.error(
                ErrorCodes.UNDEFINED_VARIABLE,
                f"Variable '{var_name}' no está definida",
                loc.file, loc.line, loc.col
            )


def analyze(ast: Stylesheet, filename: str = "<unknown>") -> List:
    """Función de conveniencia para analizar un AST"""
    analyzer = SemanticAnalyzer(filename)
    return analyzer.analyze(ast)
