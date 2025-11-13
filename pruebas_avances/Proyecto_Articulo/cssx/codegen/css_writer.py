def generate_css(ast):
    """
    Convierte el AST en CSS plano.
    """
    lines = []
    for node in ast:
        if node.kind == "ASSIGN":
            lines.append(f"{node.key}: {node.value};")
        elif node.kind == "BLOCK":
            lines.append(f"{node.key} {{")
            for n in node.value:
                lines.append(f"  {n.key}: {n.value};")
            lines.append("}")
    return "\n".join(lines)