import ast
from parser import parse
from evaluator import e  

def read_test_cases(file_path):
    test_cases = []
    with open(file_path, 'r') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line or '|' not in line:
                print(f"Error in line {line_number} in {file_path}: {line}")
                continue  # Skip to the next line instead of exiting

            expression, expected_result = line.split('|', 1)
            expression = expression.strip()
            expected_result = expected_result.strip()

            if expected_result.lower() == "true":  # Handling boolean entries
                expected_result = True
            elif expected_result.lower() == "false":
                expected_result = False
            elif expected_result.isdigit():  # Handling int
                expected_result = int(expected_result)
            elif expected_result.startswith("[") and expected_result.endswith("]"):  # Handling lists
                try:
                    expected_result = ast.literal_eval(expected_result)
                    if not isinstance(expected_result, list):
                        raise ValueError  # Ensure it's actually a list
                except (SyntaxError, ValueError):
                    print(f"Error in line {line_number} in {file_path}: {line}")
                    continue  
            else:
                try:
                    float_value = float(expected_result)
                    if '.' in expected_result:  # Ensure it's a float, not an int
                        expected_result = float_value
                    else:
                        expected_result = int(float_value)
                except ValueError:
                    if expected_result.lower() != "error":  # Allow only "error" as a string
                        print(f"Error in line {line_number} in {file_path}: {line}")
                        continue  

            test_cases.append((expression, expected_result))

    return test_cases


def run_tests(test_cases):
    for line_number, (expression, expected) in enumerate(test_cases, start=1):
        try:
            result = e(parse(expression))

            if expected == "error":
                print(f"Test failed in line {line_number}: {expression} => Expected an error, but got {result}")
                return

            # Ensure type match between result and expected
            if type(result) != type(expected):
                print(f"Test failed in line {line_number}: {expression} => Expected {expected} ({type(expected).__name__}), but got {result} ({type(result).__name__})")
                return

            # If numeric, allow small floating-point errors
            if isinstance(expected, (int, float)) and abs(result - expected) > 1e-9:
                print(f"Test failed in line {line_number}: {expression} => Expected {expected}, but got {result}")
                return

            # Handle lists comparison
            if isinstance(expected, list):
                if result != expected:
                    print(f"Test failed in line {line_number}: {expression} => Expected {expected}, but got {result}")
                    return

            # Non-numeric results (bool) must match exactly
            if isinstance(expected, bool) and result != expected:
                print(f"Test failed in line {line_number}: {expression} => Expected {expected}, but got {result}")
                return

        except Exception as error:
            if expected == "error":
                continue  # Move to the next test case
            else:
                print(f"Error in line {line_number} for expression {expression}: {error}")
                return

    print("All test cases passed")

if __name__ == '__main__':
    test_cases_file = 'test_cases.txt'
    test_cases = read_test_cases(test_cases_file)
    run_tests(test_cases)
