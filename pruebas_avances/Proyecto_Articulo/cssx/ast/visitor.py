from typing import Any
import json

class Visitor:
    def visit(self, node):
        method = getattr(self, f"visit_{node.__class__.__name__}", self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        if hasattr(node, '__dataclass_fields__'):
            for field in node.__dataclass_fields__:
                val = getattr(node, field)
                if isinstance(val, (list, tuple)):
                    for x in val:
                        if hasattr(x, '__dataclass_fields__'):
                            self.visit(x)
                elif hasattr(val, '__dataclass_fields__'):
                    self.visit(val)

class AstPrinter(Visitor):
    def __init__(self):
        self.level = 0

    def indent(self):
        return "  " * self.level

    def print(self, node):
        self.level = 0
        self.visit(node)

    def visit_Stylesheet(self, node):
        print(f"{self.indent()}Stylesheet (loc={node.loc})")
        self.level += 1
        for child in node.children:
            self.visit(child)
        self.level -= 1

    def visit_RuleSet(self, node):
        sel = ", ".join([str(s) for s in node.selectors])
        print(f"{self.indent()}RuleSet [{sel}] (loc={node.loc})")
        self.level += 1
        for decl in node.declarations:
            self.visit(decl)
        for child in node.children:
            self.visit(child)
        self.level -= 1

    def visit_Declaration(self, node):
        print(f"{self.indent()}Declaration {node.prop}: {node.value} (important={node.important}, loc={node.loc})")

    def visit_SimpleSelector(self, node):
        print(f"{self.indent()}SimpleSelector {node.kind}:{node.value} (loc={node.loc})")

    def visit_CompoundSelector(self, node):
        print(f"{self.indent()}CompoundSelector (loc={node.loc})")
        self.level += 1
        for part in node.parts:
            self.visit(part)
        self.level -= 1

    def visit_ComplexSelector(self, node):
        print(f"{self.indent()}ComplexSelector '{node.combinator}' (loc={node.loc})")
        self.level += 1
        self.visit(node.left)
        self.visit(node.right)
        self.level -= 1

    def generic_visit(self, node):
        if hasattr(node, '__dataclass_fields__'):
            print(f"{self.indent()}{node.__class__.__name__} (loc={getattr(node, 'loc', '-')})")
        super().generic_visit(node)

class AstSerializer(Visitor):
    def __init__(self):
        self.result = None

    def to_dict(self, node):
        return self.visit(node)

    def visit(self, node):
        if hasattr(node, '__dataclass_fields__'):
            result = {"type": node.__class__.__name__}
            for field in node.__dataclass_fields__:
                val = getattr(node, field)
                if hasattr(val, '__dataclass_fields__'):
                    result[field] = self.visit(val)
                elif isinstance(val, (list, tuple)):
                    result[field] = [self.visit(x) if hasattr(x, '__dataclass_fields__') else x for x in val]
                else:
                    result[field] = val
            return result
        else:
            return node

    def to_json(self, node, **kwargs):
        return json.dumps(self.to_dict(node), indent=2, **kwargs)
