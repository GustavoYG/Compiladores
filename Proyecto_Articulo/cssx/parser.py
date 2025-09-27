from .lexer import tokenize
from .ast.nodes import ASTNode

def parse(source):
    """
    Parser simple: convierte tokens en un árbol muy básico (lista de nodos).
    """
    tokens = tokenize(source)
    ast = []
    i = 0
    while i < len(tokens):
        tok, val, lineno = tokens[i]
        if tok == "KEY":
            key = val
            if i+2 < len(tokens) and tokens[i+1][0] == "EQUAL" and tokens[i+2][0] == "VALUE":
                value = tokens[i+2][1]
                ast.append(ASTNode("ASSIGN", key, value, lineno))
                i += 3
            else:
                i += 1
        elif tok == "SELECTOR":
            selector = val
            block = []
            i += 1  # saltar SELECTOR
            if i < len(tokens) and tokens[i][0] == "LBRACE":
                i += 1  # saltar LBRACE
            # Leer hasta RBRACE
            while i < len(tokens) and tokens[i][0] != "RBRACE":
                if tokens[i][0] == "KEY":
                    key = tokens[i][1]
                    if i+2 < len(tokens) and tokens[i+1][0] == "EQUAL" and tokens[i+2][0] == "VALUE":
                        value = tokens[i+2][1]
                        block.append(ASTNode("ASSIGN", key, value, tokens[i][2]))
                        i += 3
                    else:
                        i += 1
                else:
                    i += 1
            ast.append(ASTNode("BLOCK", selector, block, lineno))
            i += 1  # saltar RBRACE
        else:
            i += 1
    return ast