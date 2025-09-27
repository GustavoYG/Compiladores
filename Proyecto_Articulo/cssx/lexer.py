import re

def tokenize(source):
    """
    Tokeniza el código CSSX línea por línea, detectando claves, valores y bloques.
    """
    tokens = []
    for lineno, line in enumerate(source.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        # Bloques
        if line.endswith("{"):
            tokens.append(("LBRACE", "{", lineno))
            tokens.append(("SELECTOR", line[:-1].strip(), lineno))
        elif line == "}":
            tokens.append(("RBRACE", "}", lineno))
        # Asignaciones
        elif "=" in line:
            key, value = line.split("=", 1)
            tokens.append(("KEY", key.strip(), lineno))
            tokens.append(("EQUAL", "=", lineno))
            tokens.append(("VALUE", value.strip(), lineno))
        else:
            tokens.append(("UNKNOWN", line, lineno))
    return tokens