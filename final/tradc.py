# tradc.py
# Traductor CSSX refactorizado - Mantiene la misma interfaz pública

from cssx.lexer.dictionaries import SELECTORES_HTML_ESTANDAR, COLORES, DICCIONARIO_CSS, DICCIONARIO_HTML
from cssx.parser.syntactic import parse_bloque_css
from cssx.codegen.css_generator import traducir_a_css
from cssx.codegen.html_generator import traducir_a_html, generar_html_completo
from cssx.server.file_manager import cargar_archivo_txt, guardar_archivo, vista_previa_html, crear_archivo_ejemplo
from cssx.parser.cssx_parser import parse_to_ast
from cssx.ast.nodes import Stylesheet, VariableDecl, TemplateDef, Declaration, RuleSet
from cssx.semantics.analyzer import analyze
from cssx.semantics.diagnostics import Diagnostic


class TraductorCSSHTML:
    def __init__(self):
        # Referencias a los diccionarios para mantener compatibilidad
        self.selectores_html_estandar = SELECTORES_HTML_ESTANDAR
        self.colores = COLORES
        self.diccionario_css = DICCIONARIO_CSS
        self.diccionario_html = DICCIONARIO_HTML
        
        # Estructura HTML que se va construyendo
        self.html_elements = []
        self.html_title = "Página Generada"

    def cargar_archivo_txt(self, ruta_archivo):
        """
        Carga el contenido de un archivo de texto plano
        """
        return cargar_archivo_txt(ruta_archivo)

    def guardar_archivo(self, contenido, ruta_archivo):
        """
        Guarda el contenido traducido en un archivo
        """
        return guardar_archivo(contenido, ruta_archivo)

    def traducir_a_css(self, entrada):
        """
        Traduce el código de entrada a CSS
        """
        self.html_elements = []  # Resetear elementos HTML
        return traducir_a_css(entrada)

    def traducir_a_html(self, entrada):
        """
        Traduce el código de entrada a HTML
        """
        return traducir_a_html(entrada)

    def traducir_completo(self, entrada):
        """
        Traduce a CSS y HTML completo con expansión de plantillas
        """
        self.html_elements = []
        self.html_title = "Página Generada"

        # 1. Parsear a AST y expandir plantillas
        ast = parse_to_ast(entrada, "<input>")
        
        # 2. Expandir plantillas (antes de generar CSS)
        from cssx.semantics.templates import collect_templates, expand_templates
        tpl_table, tpl_diagnostics = collect_templates(ast)
        expansion_diagnostics = expand_templates(ast, tpl_table)
        
        # 3. Convertir AST expandido de vuelta a texto CSSX para el analizador legacy
        entrada_expandida = self._ast_to_cssx_text(ast)
        
        # 4. Generar CSS usando el analizador legacy
        css_content = self.traducir_a_css(entrada_expandida)

        # 5. Generar HTML del body usando entrada original (preserva texto=)
        html_body = self.traducir_a_html(entrada)

        # Extraer título de página si está definido
        lineas = [l.strip() for l in entrada.strip().split('\n')]
        variables = {}
        
        # Buscar titulo_pagina en las primeras líneas
        for linea in lineas:
            if "titulo_pagina" in linea and "=" in linea:
                try:
                    from analizador_sintactico import analizar_linea
                    clave, valor = analizar_linea(linea, variables)
                    if clave == "titulo_pagina":
                        self.html_title = valor
                        break
                except:
                    pass

        # Generar HTML completo
        html_completo = generar_html_completo(css_content, html_body, self.html_title)

        # Recopilar todos los errores
        all_errors = []
        if tpl_diagnostics:
            all_errors.extend([d.message for d in tpl_diagnostics])
        if expansion_diagnostics:
            all_errors.extend([d.message for d in expansion_diagnostics])

        return {
            'css': css_content,
            'html': html_completo,
            'errores': all_errors
        }

    def _ast_to_cssx_text(self, ast: Stylesheet) -> str:
        """
        Convierte un AST expandido de vuelta a texto CSSX para el analizador legacy.
        Omite las definiciones de plantillas ya que han sido expandidas.
        """
        lines = []
        
        for child in ast.children:
            if isinstance(child, VariableDecl):
                # Variables globales
                lines.append(f"{child.name} = {self._value_to_text(child.value)}")
            elif hasattr(child, 'prop') and hasattr(child, 'value'):  # Declaration
                # Declaraciones globales como titulo_pagina
                lines.append(f"{child.prop} = {self._value_to_text(child.value)}")
            elif hasattr(child, 'selectors') and hasattr(child, 'declarations'):  # RuleSet
                # Rulesets CSS
                selector_text = self._selector_to_text(child.selectors[0] if child.selectors else "")
                lines.append(f"{selector_text} {{")
                
                for decl in child.declarations:
                    if hasattr(decl, 'prop') and hasattr(decl, 'value'):
                        lines.append(f"  {decl.prop} = {self._value_to_text(decl.value)}")
                
                # Procesar rulesets anidados recursivamente
                for nested in child.children:
                    if hasattr(nested, 'selectors'):
                        nested_selector = self._selector_to_text(nested.selectors[0] if nested.selectors else "")
                        lines.append(f"  {nested_selector} {{")
                        for nested_decl in nested.declarations:
                            if hasattr(nested_decl, 'prop') and hasattr(nested_decl, 'value'):
                                lines.append(f"    {nested_decl.prop} = {self._value_to_text(nested_decl.value)}")
                        lines.append("  }")
                
                lines.append("}")
            # Omitir TemplateDef - ya fueron expandidas
        
        return '\n'.join(lines)
        
    def _value_to_text(self, value) -> str:
        """Convierte un valor AST a texto"""
        if hasattr(value, 'name'):  # VariableRef  
            return value.name
        elif hasattr(value, 'text'):  # String
            return f'"{value.text}"'
        elif hasattr(value, 'name_or_hex'):  # ColorLiteral
            return value.name_or_hex
        elif hasattr(value, 'n') and hasattr(value, 'unit'):  # Dimension
            return f"{value.n}{value.unit}"
        elif hasattr(value, 'n'):  # Number, Percentage
            # Para Number sin unidad, añadir 'px' si parece ser una dimensión
            val = str(value.n)
            if val.endswith('.0'):  # Quitar .0 de números enteros
                val = val[:-2]
            return val
        elif hasattr(value, 'value'):  # Otros tipos con value
            return str(value.value)
        elif hasattr(value, 'items'):  # SpaceList
            return ' '.join(self._value_to_text(item) for item in value.items)
        else:
            return str(value)
    
    def _selector_to_text(self, selector) -> str:
        """Convierte un selector AST a texto"""
        if hasattr(selector, 'value'):
            # Reconstruir el selector según su tipo
            if hasattr(selector, 'kind'):
                if selector.kind == 'class':
                    return f'.{selector.value}'
                elif selector.kind == 'id':
                    return f'#{selector.value}'
                else:
                    return selector.value
            else:
                return selector.value
        else:
            return str(selector)

    def obtener_ast(self, texto: str, archivo: str = "<unknown>") -> Stylesheet:
        """
        Método opcional para obtener el AST del código CSSX
        No afecta el flujo de compilación existente
        """
        return parse_to_ast(texto, archivo)

    def chequear(self, texto: str, archivo: str = "<unknown>") -> list[Diagnostic]:
        """
        Realiza análisis semántico del código CSSX y retorna diagnósticos
        No afecta el flujo de compilación normal
        """
        try:
            ast = parse_to_ast(texto, archivo)
            diagnosticos = analyze(ast, archivo)
            return diagnosticos
        except Exception as e:
            # Si hay error de parsing, crear diagnóstico de error
            from semantica_diagnosticos import Diagnostic, ErrorCodes
            return [Diagnostic(
                code=ErrorCodes.INVALID_VALUE,
                severity="ERROR",
                message=f"Error de análisis: {str(e)}",
                file=archivo,
                line=1,
                col=1
            )]

    def traducir_desde_archivo(self, ruta_archivo, tipo_salida="completo", guardar_css=None, guardar_html=None):
        """
        Traduce desde un archivo con opción de salida completa
        """
        contenido = self.cargar_archivo_txt(ruta_archivo)

        if tipo_salida.lower() == "css":
            resultado = self.traducir_a_css(contenido)
            if guardar_css:
                self.guardar_archivo(resultado, guardar_css)
            return resultado
        elif tipo_salida.lower() == "html":
            resultado = self.traducir_a_html(contenido)
            if guardar_html:
                self.guardar_archivo(resultado, guardar_html)
            return resultado
        elif tipo_salida.lower() == "completo":
            resultado = self.traducir_completo(contenido)
            css_resultado, html_resultado = resultado['css'], resultado['html']
            if guardar_css:
                self.guardar_archivo(css_resultado, guardar_css)
            if guardar_html:
                self.guardar_archivo(html_resultado, guardar_html)
            return resultado
        else:
            raise ValueError("tipo_salida debe ser 'css', 'html' o 'completo'")

    def vista_previa_html(self, archivo_cssx, titulo="Vista previa"):
        """
        Genera automáticamente HTML con CSS traducido y lo abre en el navegador
        """
        try:
            # Cargar y traducir contenido
            contenido = self.cargar_archivo_txt(archivo_cssx)
            resultado = self.traducir_completo(contenido)
            css_content, html_completo = resultado['css'], resultado['html']

            # Usar la función del gestor de archivos
            vista_previa_html(archivo_cssx, html_completo, titulo)

        except Exception as e:
            print(f"Error al generar vista previa: {e}")

    def crear_archivo_ejemplo(self, nombre_archivo="ejemplo.cssx"):
        """
        Crea un archivo de ejemplo para probar el traductor
        """
        return crear_archivo_ejemplo(nombre_archivo)


# ==============================================================================
if __name__ == "__main__":
    import sys
    
    traductor = TraductorCSSHTML()

    # Verificar si se proporcionó un archivo como argumento
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
        print(f"=== PROCESANDO ARCHIVO: {archivo_entrada} ===")
        
        try:
            # Traducir desde archivo especificado
            resultado = traductor.traducir_desde_archivo(
                archivo_entrada,
                tipo_salida="completo"
            )
            css_resultado, html_resultado = resultado['css'], resultado['html']
            
            print("\n=== CSS GENERADO ===")
            print(css_resultado)
            
            print("\n=== ERRORES ===")
            print(resultado.get('errores', []))
            
        except Exception as e:
            print(f"Error procesando archivo: {e}")
            
        sys.exit(0)

    # Crear archivo de ejemplo (comportamiento por defecto)
    archivo_ejemplo = traductor.crear_archivo_ejemplo("mi_estilo.cssx")

    print("=== EJEMPLO DE TRADUCCIÓN COMPLETA ===")

    try:
        # Traducir desde archivo
        resultado = traductor.traducir_desde_archivo(
            archivo_ejemplo,
            tipo_salida="completo",
            guardar_css="styles.css",
            guardar_html="index.html"
        )
        css_resultado, html_resultado = resultado['css'], resultado['html']

        print("\n=== CSS GENERADO ===")
        print(css_resultado)

        print("\n=== HTML GENERADO ===")
        print(html_resultado)

        # Generar vista previa
        print("\n=== GENERANDO VISTA PREVIA ===")
        traductor.vista_previa_html(archivo_ejemplo)

    except Exception as e:
        print(f"Error: {e}")

    # Ejemplo directo también funciona
    print("\n=== EJEMPLO DIRECTO ===")
    ejemplo_directo = '''
    titulo_pagina = "Ejemplo Directo"

    body {
      fondo = negro
      color = blanco
    }

    .contenedor {
      ancho = 300
      alto = 200
      fondo = rojo
      margen = 20 auto
    }

    .contenedor parrafo {
      texto = "Contenido del párrafo"
      color = amarillo
      alinear = center
    }
    '''

    resultado_directo = traductor.traducir_completo(ejemplo_directo)
    css_directo, html_directo = resultado_directo['css'], resultado_directo['html']
    print("CSS:")
    print(css_directo)
    print("\nHTML:")
    print(html_directo)
