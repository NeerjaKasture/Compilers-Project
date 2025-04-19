keywords = ["if", "elif", "else", "nocap", "cap", "yap", "concat", "while", "for", "and", "or", "not", "def", "yeet", "void", "break", "continue","spill","fn", "stack", "queue","hashmap"]

from dataclasses import dataclass

class AST:
    pass

@dataclass
class Function(AST):
    name: str
    params: list[tuple[str, str]]  # List of (type, name) pairs
    return_type: str
    body: AST 

datatypes = {
    "int": int, 
    "float": float, 
    "bool": bool, 
    "string": str,
    "int[]": list,
    "float[]": list,
    "bool[]": list,
    "string[]": list,
    "fn": Function,
    "fn[]": Function,
    "void": None,
}

