import sys
import os
from lexer import lex
from parser import parse, ParseError
from evaluator import e
from typechecker import TypeChecker

if len(sys.argv) != 2:
    print("Usage: python compiler.py <filename.yap>")
    sys.exit(1)

filename = sys.argv[1]

# Check file extension
if not filename.endswith('.yap'):
    print("Error: Input file must have a .yap extension")
    sys.exit(1)

try:
    with open(filename, 'r', encoding='utf-8') as file:
        code = file.read()
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)
except IOError as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

ast = parse(code)
# print(ast)
checker = TypeChecker()
checker.visit(ast)
try:
    result = e(ast)
    # result
except Exception as e:
    print(f"Error during compilation: {e}")
    sys.exit(1)