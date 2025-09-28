# generador_css.py
# Funciones para generar código CSS desde el código CSSX parseado

from analizador_sintactico import parse_bloque_css


def traducir_a_css(entrada):
    """
    Traduce el código de entrada a CSS
    """
    html_elements = []  # Lista para almacenar elementos HTML extraídos
    lineas = [l.strip() for l in entrada.strip().split('\n')]
    return parse_bloque_css(lineas, html_elements=html_elements)
