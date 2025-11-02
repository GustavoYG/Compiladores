# gestor_archivos.py
# Funciones para el manejo de archivos (cargar, guardar, vista previa)

import os
import webbrowser
import tempfile
from pathlib import Path


def cargar_archivo_txt(ruta_archivo):
    """
    Carga el contenido de un archivo de texto plano
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            return archivo.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    except Exception as e:
        raise Exception(f"Error al leer el archivo: {e}")


def guardar_archivo(contenido, ruta_archivo):
    """
    Guarda el contenido traducido en un archivo
    """
    try:
        # Crear directorio si no existe
        Path(ruta_archivo).parent.mkdir(parents=True, exist_ok=True)

        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
        return True
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return False


def vista_previa_html(archivo_cssx, html_completo, titulo="Vista previa"):
    """
    Genera automáticamente HTML con CSS traducido y lo abre en el navegador
    """
    try:
        # Guardar HTML en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_html:
            temp_html.write(html_completo)
            ruta_html = temp_html.name

        # Abrir en el navegador
        webbrowser.open(f"file://{ruta_html}")
        print(f"Vista previa generada y abierta: {ruta_html}")

    except Exception as e:
        print(f"Error al generar vista previa: {e}")


def crear_archivo_ejemplo(nombre_archivo="ejemplo.cssx"):
    """
    Crea un archivo de ejemplo para probar el traductor
    """
    contenido_ejemplo = '''titulo_pagina = "Mi Página Web"

@color_principal = azul
@fuente_principal = Arial, sans-serif
@tamaño_base = 16

body {
  fondo = @color_principal
  color = blanco
  tamano = @tamaño_base
  margen = 0
  relleno = 20
  fuente = @fuente_principal
  alinear = center
}

parrafo {
  texto = "¡Hola mundo desde mi propio compilador CSS!"
  tamano = 18
  margen = 20 0
}

boton {
  texto = "Haz clic aquí"
  relleno = 10 20
  fondo = naranja
  color = blanco
  borde = none
  redondeado = 5
  cursor = pointer
  tamano = 16
}

.caja {
  fondo = blanco
  color = negro
  margen = 40 auto
  relleno = 20
  ancho = 80%
  borde = 1px solid gris
  redondeado = 10
  sombra = 0 4px 8px rgba(0,0,0,0.1)

  titulo {
    texto = "Este es un título dentro de .caja"
    tamano = 24
    color = rojo
    alinear = center
    peso = bold
    margen = 0 0 15 0
  }

  enlace {
    texto = "Este es un enlace dentro de .caja"
    decoracion = underline
    color = azul
    mostrar = block
    margen = 10 0
  }
}

.boton {
  texto = "Esto es un botón simulado con la clase .boton"
  relleno = 15 25
  fondo = verde
  color = blanco
  redondeado = 8
  margen = 20 auto
  mostrar = inline-block
  cursor = pointer
  transicion = all 0.3s ease
}'''

    guardar_archivo(contenido_ejemplo, nombre_archivo)
    print(f"Archivo de ejemplo creado: {nombre_archivo}")
    return nombre_archivo
