import sys
import os
from lexer import lex
from parser import parse
# Import evaluator correctly - ensure the function name is correct
try:
    from evaluator import evaluate as e  # Use the actual function name from your evaluator module
except ImportError:
    # If the function name is different, try importing the module directly
    import evaluator
    e = evaluator.e  # Assuming the function is named 'e' in the module

from typechecker import TypeChecker
from errors import handle_error

# Custom exception hook to suppress traceback
def custom_excepthook(exc_type, exc_value, exc_traceback):
    # If it's one of our custom exceptions, just print the error message
    if exc_type.__module__ == 'errors':
        print(f"ERROR: {exc_value}")
        sys.exit(1)
    else:
        # For other exceptions use the default exception handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Install the custom exception hook
sys.excepthook = custom_excepthook

def check_for_common_issues(code):
    """Check for common coding issues before compiling"""
    lines = code.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        # Check for missing semicolons
        if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}'):
            if not any(keyword in line for keyword in ['if', 'else', 'while', 'for']):
                print(f"WARNING: Line {i+1} may be missing a semicolon: '{line}'")
        
        # Check for variable declaration followed by usage
        if '=' in line and ';' in line:
            parts = line.split('=')[0].strip().split()
            if len(parts) >= 2:
                var_type, var_name = parts[0], parts[1].rstrip(';')
                # Check next lines for immediate usage
                for next_line in lines[i+1:i+3]:  # Check next 2 lines
                    if var_name + '2' in next_line:
                        print(f"WARNING: Line {i+1}: You declared '{var_name}' but used '{var_name}2' later")
                        break
    
    return True  # Continue with compilation

def main():
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
    except IOError as error:
        print(f"Error reading file: {error}")
        sys.exit(1)

    try:
        # Parse the code
        ast = parse(code)
        if ast is None:
            # A parse error occurred that was already handled
            print("ERROR: Failed to parse the code. Please fix the syntax errors.")
            sys.exit(1)
        
        # Check for common code issues before typechecking
        if check_for_common_issues(code):
            # Continue only if no major issues found
            
            # Check types
            checker = TypeChecker()
            checker.visit(ast)
            
            # Evaluate/execute the program
            try:
                result = e(ast)
            except NameError as err:
                print(f"ERROR: Evaluator function not properly imported: {err}")
                sys.exit(1)
            # Successfully completed
    except Exception as exc:
        # Any unhandled exceptions are passed to our custom handler
        handle_error(exc)

if __name__ == "__main__":
    main()