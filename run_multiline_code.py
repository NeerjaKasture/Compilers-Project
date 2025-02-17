import ast
from parser import e, parse

def run_tests(expression, expected):
    try:
        result = e(parse(expression))

        if expected == "error":
            print(f"Test failed: {expression} => Expected an error, but got {result}")
            return

        # Ensure type match
        if type(result) != type(expected):
            print(f"Test failed: {expression} => Expected {expected} ({type(expected).__name__}), but got {result} ({type(result).__name__})")
            return

        # Allow small floating-point errors
        if isinstance(expected, (int, float)) and abs(result - expected) > 1e-9:
            print(f"Test failed: {expression} => Expected {expected}, but got {result}")
            return

        # Handle list comparison
        if isinstance(expected, list) and result != expected:
            print(f"Test failed: {expression} => Expected {expected}, but got {result}")
            return

        # Non-numeric results (bool) must match exactly
        if isinstance(expected, bool) and result != expected:
            print(f"Test failed: {expression} => Expected {expected}, but got {result}")
            return

    except Exception as error:
        if expected == "error":
            return
        else:
            print(f"Error in expression {expression}: {error}")
            return

    print("Test case passed successfully")

with open('multiline_code.txt', 'r') as code:
    test_case = code.read()           # Read the entire file as a single string

# print(e(parse(test_case)))          # debugging output

expected = [5, 6, 15]                 # write the expected output of code.txt
run_tests(test_case, expected)  
