# Helper para imprimir AST
def print_tree(ast, indent=0):
    for node in ast:
        print("  " * indent + f"{node.type}: {node.value}")
        if hasattr(node, "children"):
            print_tree(node.children, indent+1)