import ast
from typing import List, Optional
from .models import SymbolNode, FileContext

class Skeletonizer:
    """
    Transforms raw source code into lightweight structural AST skeletons,
    stripping function bodies while preserving signatures, docstrings, and classes.
    """
    def __init__(self, preserve_docstrings: bool = True):
        self.preserve_docstrings = preserve_docstrings

    def process_file(self, path: str, content: str) -> FileContext:
        """Parses a file and extracts all top-level and method symbol definitions."""
        if not content.strip():
            return FileContext(path=path, symbols=[], total_tokens=0, pruned_tokens=0)

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return FileContext(path=path, symbols=[], total_tokens=len(content.split()), pruned_tokens=len(content.split()))

        symbols = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [arg.arg for arg in node.args.args]
                sig = f"{'async ' if isinstance(node, ast.AsyncFunctionDef) else ''}def {node.name}({', '.join(args)})"
                doc = ast.get_docstring(node) if self.preserve_docstrings else None
                sig_tokens = len(sig.split()) + (len(doc.split()) if doc else 0)
                symbols.append(SymbolNode(
                    name=node.name,
                    type=type(node).__name__,
                    signature=sig,
                    token_count=len(ast.unparse(node).split()),
                    pruned_token_count=sig_tokens,
                    docstring=doc
                ))
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) for b in node.bases]
                base_str = f"({', '.join(bases)})" if bases else ""
                sig = f"class {node.name}{base_str}"
                doc = ast.get_docstring(node) if self.preserve_docstrings else None
                sig_tokens = len(sig.split()) + (len(doc.split()) if doc else 0)
                symbols.append(SymbolNode(
                    name=node.name,
                    type=type(node).__name__,
                    signature=sig,
                    token_count=len(ast.unparse(node).split()),
                    pruned_token_count=sig_tokens,
                    docstring=doc
                ))

        total_tokens = len(content.split())
        pruned_tokens = sum(s.pruned_token_count for s in symbols) if symbols else total_tokens
        return FileContext(
            path=path,
            symbols=symbols,
            total_tokens=total_tokens,
            pruned_tokens=pruned_tokens
        )

    def skeletonize(self, content: str) -> str:
        """Strips implementation bodies of functions/methods, replacing them with ellipses."""
        if not content.strip():
            return ""

        tree = ast.parse(content)
        
        class PruningTransformer(ast.NodeTransformer):
            def __init__(self, preserve_doc: bool):
                self.preserve_doc = preserve_doc

            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                self.generic_visit(node)
                doc = ast.get_docstring(node)
                new_body = []
                if self.preserve_doc and doc:
                    new_body.append(ast.Expr(value=ast.Constant(value=doc)))
                new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
                node.body = new_body
                return node

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
                self.generic_visit(node)
                doc = ast.get_docstring(node)
                new_body = []
                if self.preserve_doc and doc:
                    new_body.append(ast.Expr(value=ast.Constant(value=doc)))
                new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
                node.body = new_body
                return node

        transformer = PruningTransformer(self.preserve_docstrings)
        pruned_tree = transformer.visit(tree)
        return ast.unparse(pruned_tree)