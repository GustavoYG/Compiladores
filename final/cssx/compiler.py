# cssx/compiler.py

from cssx.parser.cssx_parser import parse_to_ast, ParseError
from cssx.semantics.analyzer import SemanticAnalyzer, VariableResolver
from cssx.codegen.ast_css_generator import AstCssGenerator
from cssx.codegen.ast_html_generator import AstHtmlGenerator
from cssx.semantics.diagnostics import Diagnostic

class Compiler:
    """
    A new compiler that orchestrates the parsing, semantic analysis,
    and code generation from the AST.
    """
    def __init__(self):
        pass

    def compile(self, code: str, filename: str = "<input>"):
        """
        Compiles CSSX code to CSS and HTML.
        """
        diagnostics = []
        
        # 1. Parsing
        try:
            ast = parse_to_ast(code, filename)
        except Exception as e:
            diagnostics.append(Diagnostic(
                "ERROR", "E0001", f"Error de Parseo: {e}", filename, getattr(e, 'loc', (1,1))[0], getattr(e, 'loc', (1,1))[1]
            ))
            return self._build_result(success=False, diagnostics=diagnostics)

        # 2. Semantic Analysis
        analyzer = SemanticAnalyzer(filename)
        analysis_diagnostics, context = analyzer.analyze(ast)
        diagnostics.extend(analysis_diagnostics)

        has_errors = any(d.severity == 'ERROR' for d in diagnostics)
        if has_errors:
            return self._build_result(success=False, diagnostics=diagnostics)

        # 3. Variable Resolution
        resolver = VariableResolver(context)
        resolved_ast = resolver.resolve(ast)

        # 4. Code Generation
        try:
            css_generator = AstCssGenerator()
            css_output = css_generator.generate(resolved_ast)

            html_generator = AstHtmlGenerator()
            title, body_html = html_generator.generate(resolved_ast)
            full_html = self._create_full_html(title, css_output, body_html)

        except Exception as e:
            diagnostics.append(Diagnostic(
                "ERROR", "E0002", f"Error inesperado durante la generación de código: {e}", filename, 1, 1
            ))
            return self._build_result(success=False, diagnostics=diagnostics)

        return self._build_result(success=True, css=css_output, html=full_html, diagnostics=diagnostics)

    def _build_result(self, success, css='', html='', diagnostics=[]):
        """Helper to build the final result dictionary."""
        serializable_diagnostics = [d.to_dict() for d in diagnostics]
        return {
            'success': success,
            'css': css,
            'html': html,
            'diagnostics': serializable_diagnostics
        }

    def _create_full_html(self, title: str, css: str, body: str) -> str:
        """
        Wraps the generated body and CSS in a full HTML document.
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{body}
</body>
</html>"""

