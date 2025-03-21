import sys
from lexer import lex
from parser import parse
from evaluator import e

if len(sys.argv) != 2:
    print("Usage: python compiler.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

try:
    with open(filename, 'r', encoding='utf-8') as file:
        code = file.read()
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)


ast = parse(code)
result = e(ast)
result




