from cssx.parser import parse
from cssx.codegen.css_writer import generate_css

def test_demo():
    src = """
body {
  fondo = azul
  color = blanco
}
"""
    ast = parse(src)
    css = generate_css(ast)
    assert "body" in css
    assert "fondo" in css