class ASTVisitor:
    def visit(self, node):
        method = getattr(self, f"visit_{node.kind.lower()}", self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        if node.kind == "BLOCK":
            for n in node.value:
                self.visit(n)