import ast
from typing import List
from .models import SymbolNode, FileContext

class Skeletonizer:
    def process_file(self, path: str, content: str) -> FileContext:
        tree = ast.parse(content)
        symbols = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                sig = f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                doc = ast.get_docstring(node)
                symbols.append(SymbolNode(
                    name=node.name,
                    type=type(node).__name__,
                    signature=sig,
                    token_count=len(content.split()),
                    pruned_token_count=len(sig.split()) + (len(doc.split()) if doc else 0),
                    docstring=doc
                ))
        return FileContext(path=path, symbols=symbols, total_tokens=len(content.split()), pruned_tokens=sum(s.pruned_token_count for s in symbols))