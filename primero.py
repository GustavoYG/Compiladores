# %% [code]
def traducir_a_css(entrada):
    diccionario_css = {
        "fondo": "background-color",
        "tamaño_letra": "font-size",
        "color_texto": "color",
       
    }

    colores = {
        "azul": "blue",
        "rojo": "red",
        "verde": "green",
        "blanco": "white",
        "negro": "black",
        "amarillo": "yellow",
    
    }

    lineas = entrada.strip().split('\n')
    salida_css = []

    for linea in lineas:
        if '=' in linea:
            clave, valor = linea.split('=')
            clave = clave.strip()
            valor = valor.strip().strip('"')

            propiedad_css = diccionario_css.get(clave, clave)
            valor_css = colores.get(valor.lower(), valor)

            salida_css.append(f"{propiedad_css}: {valor_css};")

    return "\n".join(salida_css)


# Ejemplo de uso:
entrada = '''
fondo = "azul"
tamaño_letra = "16px"
color_texto = "blanco"
'''

print(traducir_a_css(entrada))