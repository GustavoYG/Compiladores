class ASTNode:
    def __init__(self, kind, key, value=None, lineno=0):
        self.kind = kind  # "ASSIGN", "BLOCK"
        self.key = key
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        if self.kind == "BLOCK":
            return f"BLOCK<{self.key}>({self.value})"
        return f"{self.kind}: {self.key} = {self.value} (L{self.lineno})"