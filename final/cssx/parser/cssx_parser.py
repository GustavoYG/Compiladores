# cssx_parser.py
# Parser que convierte código CSSX a AST

import re
from typing import List, Optional, Tuple, Union, Any
from cssx.ast.nodes import *
from cssx.lexer.dictionaries import COLORES, DICCIONARIO_CSS, DICCIONARIO_HTML, SELECTORES_HTML_ESTANDAR


class ParseError(Exception):
    """Error de parseo"""
    def __init__(self, message: str, loc: Loc):
        super().__init__(message)
        self.loc = loc


class CSSXParser:
    """Parser para código CSSX que genera AST"""
    
    def __init__(self, filename: str = "<unknown>"):
        self.filename = filename
        self.lines: List[str] = []
        self.current_line = 0
        self.current_col = 0
        self.current_offset = 0
    
    def _make_loc(self, line: Optional[int] = None, col: Optional[int] = None, offset: Optional[int] = None) -> Loc:
        """Crea un objeto Loc con la posición actual o especificada"""
        return Loc(
            file=self.filename,
            line=line if line is not None else self.current_line + 1,
            col=col if col is not None else self.current_col + 1,
            offset=offset if offset is not None else self.current_offset
        )
    
    def _parse_value(self, value_str: str, variables: dict) -> Union[Value, str]:
        """Parsea un valor CSS desde una cadena"""
        value_str = value_str.strip()
        
        # Remover comillas
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return String(text=value_str[1:-1])
        
        # Referencia a variable
        if value_str.startswith("@"):
            return VariableRef(name=value_str)
        
        # Funciones CSS (rgba, calc, etc.)
        func_match = re.match(r'^(\w+)\s*\(([^)]+)\)$', value_str)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            # Parsear argumentos básicamente
            args = tuple(arg.strip() for arg in args_str.split(','))
            return Function(name=func_name, args=args)
        
        # URL
        if value_str.startswith('url(') and value_str.endswith(')'):
            url_content = value_str[4:-1].strip()
            if url_content.startswith('"') and url_content.endswith('"'):
                url_content = url_content[1:-1]
            return Url(path=url_content)
        
        # Lista de valores separados por espacios
        tokens = value_str.split()
        if len(tokens) > 1:
            parsed_tokens = []
            for token in tokens:
                parsed_tokens.append(self._parse_single_value(token, variables))
            return SpaceList(items=tuple(parsed_tokens))
        
        # Valor único
        return self._parse_single_value(value_str, variables)
    
    def _parse_single_value(self, token: str, variables: dict) -> Union[Value, str]:
        """Parsea un valor individual"""
        token = token.strip()
        
        # Color por nombre
        if token.lower() in COLORES:
            return ColorLiteral(name_or_hex=COLORES[token.lower()])
        
        # Color hexadecimal
        if re.match(r'^#[0-9a-fA-F]{3,8}$', token):
            return ColorLiteral(name_or_hex=token)
        
        # Porcentaje
        if token.endswith('%'):
            try:
                n = float(token[:-1])
                return Percentage(n=n)
            except ValueError:
                pass
        
        # Dimensión (número + unidad)
        dim_match = re.match(r'^([-+]?\d*\.?\d+)(px|em|rem|vh|vw|pt|pc|in|cm|mm|ex|ch|vmin|vmax|s|ms)$', token)
        if dim_match:
            n = float(dim_match.group(1))
            unit = dim_match.group(2)
            return Dimension(n=n, unit=unit)
        
        # Número puro
        try:
            n = float(token)
            return Number(n=n)
        except ValueError:
            pass
        
        # Palabra clave
        return Keyword(name=token)
    
    def _parse_selector(self, selector_str: str) -> Selector:
        """Parsea un selector"""
        selector_str = selector_str.strip()
        
        # Selectors complejos con combinadores
        for combinator in [' ', '>', '+', '~']:
            if combinator in selector_str:
                parts = selector_str.split(combinator, 1)
                if len(parts) == 2:
                    left = self._parse_selector(parts[0].strip())
                    right = self._parse_selector(parts[1].strip())
                    return ComplexSelector(
                        left=left,
                        combinator=combinator,
                        right=right,
                        loc=self._make_loc()
                    )
        
        # Selector compuesto (múltiples selectores simples juntos)
        simple_parts = []
        current = selector_str
        
        while current:
            if current.startswith('.'):
                # Clase
                match = re.match(r'^\.([a-zA-Z_-][a-zA-Z0-9_-]*)', current)
                if match:
                    class_name = match.group(1)
                    simple_parts.append(SimpleSelector(kind='class', value=class_name, loc=self._make_loc()))
                    current = current[match.end():]
                else:
                    break
            elif current.startswith('#'):
                # ID
                match = re.match(r'^#([a-zA-Z_-][a-zA-Z0-9_-]*)', current)
                if match:
                    id_name = match.group(1)
                    simple_parts.append(SimpleSelector(kind='id', value=id_name, loc=self._make_loc()))
                    current = current[match.end():]
                else:
                    break
            elif current.startswith(':'):
                # Pseudo-elemento o pseudo-clase
                if current.startswith('::'):
                    match = re.match(r'^::([a-zA-Z_-]+)', current)
                    if match:
                        pseudo_name = match.group(1)
                        simple_parts.append(SimpleSelector(kind='pseudo_elem', value=pseudo_name, loc=self._make_loc()))
                        current = current[match.end():]
                    else:
                        break
                else:
                    match = re.match(r'^:([a-zA-Z_-]+)', current)
                    if match:
                        pseudo_name = match.group(1)
                        simple_parts.append(SimpleSelector(kind='pseudo', value=pseudo_name, loc=self._make_loc()))
                        current = current[match.end():]
                    else:
                        break
            else:
                # Tipo/elemento
                match = re.match(r'^([a-zA-Z_-][a-zA-Z0-9_-]*)', current)
                if match:
                    element_name = match.group(1)
                    # Traducir nombres de elementos si es necesario
                    if element_name in DICCIONARIO_HTML:
                        element_name = DICCIONARIO_HTML[element_name]
                    simple_parts.append(SimpleSelector(kind='type', value=element_name, loc=self._make_loc()))
                    current = current[match.end():]
                else:
                    break
        
        if len(simple_parts) == 1:
            return simple_parts[0]
        elif len(simple_parts) > 1:
            return CompoundSelector(parts=tuple(simple_parts), loc=self._make_loc())
        else:
            # Fallback para casos edge
            return SimpleSelector(kind='type', value=selector_str, loc=self._make_loc())
    
    def _parse_declaration(self, line: str, variables: dict) -> Union[Declaration, VariableDecl, None]:
        """Parsea una declaración o variable"""
        line = line.strip()
        
        if not line or line.startswith('#') or line.startswith('//'):
            return None
        
        # Patrón para variables: @nombre = valor
        var_match = re.match(r'^\s*(@[\w\u00C0-\u017F]+)\s*=\s*(.+)$', line)
        if var_match:
            key = var_match.group(1).strip()
            value_str = var_match.group(2).strip()
            value = self._parse_value(value_str, variables)
            return VariableDecl(name=key, value=value, loc=self._make_loc())
        
        # Patrón para declaraciones CSS: propiedad: valor
        css_match = re.match(r'^\s*([\w\u00C0-\u017F-]+)\s*:\s*(.+)$', line)
        if css_match:
            key = css_match.group(1).strip()
            value_str = css_match.group(2).strip()
            value = self._parse_value(value_str, variables)
            return Declaration(prop=key, value=value, important=False, loc=self._make_loc())
        
        # Patrón para declaraciones especiales y CSS con =: propiedad = valor
        special_match = re.match(r'^\s*([\w\u00C0-\u017F-]+)\s*=\s*(.+)$', line)
        if special_match:
            key = special_match.group(1).strip()
            value_str = special_match.group(2).strip()
            
            # Todas las declaraciones con = se tratan como declaraciones CSS/especiales
            value = self._parse_value(value_str, variables)
            return Declaration(prop=key, value=value, important=False, loc=self._make_loc())
        
        return None
    
    def _parse_block(self, lines: List[str], start_idx: int) -> Tuple[List[str], int]:
        """Extrae un bloque de código delimitado por llaves"""
        block_lines = []
        brace_count = 1
        i = start_idx
        
        while i < len(lines) and brace_count > 0:
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            if brace_count > 0:
                block_lines.append(line)
            i += 1
        
        return block_lines, i
    
    def _parse_ruleset(self, selector_line: str, block_lines: List[str], variables: dict) -> RuleSet:
        """Parsea un ruleset (selector + declaraciones + reglas anidadas)"""
        # Extraer selector de la línea
        selector_str = selector_line.split('{')[0].strip()
        selector = self._parse_selector(selector_str)
        
        declarations = []
        children = []
        
        i = 0
        while i < len(block_lines):
            line = block_lines[i].strip()
            
            if not line or line.startswith('#') or line.startswith('//'):
                i += 1
                continue
            
            # Detectar ruleset anidado
            if '{' in line and '}' not in line:
                nested_block, end_idx = self._parse_block(block_lines, i + 1)
                nested_ruleset = self._parse_ruleset(line, nested_block, variables)
                children.append(nested_ruleset)
                i = end_idx
                continue
            
            # Detectar uso de plantilla
            if line.startswith('usar '):
                template_use = self._parse_template_use(line, variables)
                declarations.append(template_use)  # TemplateUse se añade a declarations
                i += 1
                continue
            
            # Parsear declaración
            decl = self._parse_declaration(line, variables)
            if decl:
                if isinstance(decl, VariableDecl):
                    variables[decl.name] = decl.value
                elif isinstance(decl, Declaration):
                    declarations.append(decl)
            
            i += 1
        
        return RuleSet(
            selectors=[selector],
            declarations=declarations,
            children=children,
            loc=self._make_loc()
        )
    
    def _parse_template_def(self, header_line: str, body_lines: List[str], variables: dict) -> TemplateDef:
        """Parsea definición de plantilla: plantilla NOMBRE(@params) { ... }"""
        # Extraer nombre y parámetros del header
        # Formato: "plantilla NOMBRE(@p1=default1, @p2, @p3=default3) {"
        header = header_line.replace('{', '').strip()
        parts = header.split('(', 1)
        
        if len(parts) < 2:
            # Sin parámetros: "plantilla NOMBRE {"
            name = header.replace('plantilla ', '').strip()
            params = []
        else:
            # Con parámetros: "plantilla NOMBRE(@p1, @p2=val) {"
            name = parts[0].replace('plantilla ', '').strip()
            params_str = parts[1].rstrip(')')
            params = self._parse_template_params(params_str, variables)
        
        # Parsear cuerpo (declaraciones)
        body = []
        for line in body_lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                decl = self._parse_declaration(line, variables)
                if decl and isinstance(decl, Declaration):
                    body.append(decl)
        
        return TemplateDef(name=name, params=params, body=body, loc=self._make_loc())
    
    def _parse_template_params(self, params_str: str, variables: dict) -> List[Param]:
        """Parsea lista de parámetros de plantilla: @p1=default, @p2, @p3=val"""
        if not params_str.strip():
            return []
        
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if not param:
                continue
            
            if '=' in param:
                # Parámetro con valor por defecto: @p=valor
                name, default_str = param.split('=', 1)
                name = name.strip()
                default_value = self._parse_value(default_str.strip(), variables)
                params.append(Param(name=name, default_value=default_value, loc=self._make_loc()))
            else:
                # Parámetro sin valor por defecto: @p
                name = param.strip()
                params.append(Param(name=name, default_value=None, loc=self._make_loc()))
        
        return params
    
    def _parse_template_use(self, line: str, variables: dict) -> TemplateUse:
        """Parsea uso de plantilla: usar NOMBRE(args)"""
        # Extraer nombre y argumentos
        # Formato: "usar NOMBRE(arg1, arg2, @p=val)"
        line = line.replace('usar ', '').strip()
        
        if '(' not in line:
            # Sin argumentos: "usar NOMBRE"
            name = line.strip()
            args = []
        else:
            # Con argumentos: "usar NOMBRE(arg1, @p=val)"
            name = line.split('(')[0].strip()
            args_str = line.split('(', 1)[1].rstrip(')')
            args = self._parse_template_args(args_str, variables)
        
        return TemplateUse(name=name, args=args, loc=self._make_loc())
    
    def _parse_template_args(self, args_str: str, variables: dict) -> List[Union[Value, NamedArg]]:
        """Parsea argumentos de uso de plantilla: arg1, arg2, @p=val"""
        if not args_str.strip():
            return []
        
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            if not arg:
                continue
            
            if '=' in arg and arg.startswith('@'):
                # Argumento nombrado: @p=valor
                name, value_str = arg.split('=', 1)
                name = name.strip()
                value = self._parse_value(value_str.strip(), variables)
                args.append(NamedArg(name=name, value=value, loc=self._make_loc()))
            else:
                # Argumento posicional: valor
                value = self._parse_value(arg, variables)
                args.append(value)
        
        return args
    
    def parse_to_ast(self, text: str) -> Stylesheet:
        """Parsea código CSSX a AST"""
        self.lines = text.strip().split('\n')
        self.current_line = 0
        self.current_offset = 0
        
        variables = {}
        children = []
        
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            self.current_line = i
            
            if not line or line.startswith('#') or line.startswith('//'):
                i += 1
                continue
            
            # Detectar definición de plantilla
            if line.startswith('plantilla ') and '{' in line:
                block_lines, end_idx = self._parse_block(self.lines, i + 1)
                template_def = self._parse_template_def(line, block_lines, variables)
                children.append(template_def)
                i = end_idx
                continue
            
            # Detectar ruleset
            if '{' in line and '}' not in line:
                block_lines, end_idx = self._parse_block(self.lines, i + 1)
                ruleset = self._parse_ruleset(line, block_lines, variables)
                children.append(ruleset)
                i = end_idx
                continue
            
            # Parsear declaración o variable global
            decl = self._parse_declaration(line, variables)
            if decl:
                if isinstance(decl, VariableDecl):
                    variables[decl.name] = decl.value
                    children.append(decl)
                elif isinstance(decl, Declaration):
                    # Declaraciones globales como titulo_pagina
                    children.append(decl)
            
            i += 1
        
        return Stylesheet(children=children, loc=self._make_loc(1, 1, 0))


def parse_to_ast(text: str, filename: str = "<unknown>") -> Stylesheet:
    """Función de conveniencia para parsear código CSSX a AST"""
    parser = CSSXParser(filename)
    return parser.parse_to_ast(text)
