# CSSX Modularizado

Compilador y servidor hot-reload para CSSX (CSS en español).

## Instalación y Uso

```bash
pip install -e .
```

### Compilar un archivo CSSX
```bash
cssx build examples/demo.cssx -o style.css
```

### Servir con hot-reload
```bash
cssx serve examples/demo.cssx
```

Verifica `tests/test_smoke.py` para un test de humo.

---

## Estructura propuesta

- `cssx/` : Código fuente modular
- `examples/`: Ejemplos CSSX
- `tests/`: Pruebas automáticas
