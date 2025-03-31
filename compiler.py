import sys
from parser import parse
from evaluator import e
from typechecker import TypeChecker

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
checker = TypeChecker()
checker.visit(ast)

result = e(ast)
result
