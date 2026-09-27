from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SymbolNode:
    name: str
    type: str
    signature: str
    token_count: int
    pruned_token_count: int
    docstring: Optional[str] = None

@dataclass
class FileContext:
    path: str
    symbols: List[SymbolNode]
    total_tokens: int
    pruned_tokens: int