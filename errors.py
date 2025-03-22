
# Description: Contains custom exceptions for the interpreter
class ParseError(Exception):
    def __init__(self, message, token):
        super().__init__(f"Error : {message}")
        self.token = token
        self.message = message

class TypeError(Exception):
    def __init__(self, expected, actual):
        super().__init__(f"Type error: expected {expected}, got {actual}")
        self.expected = expected
        self.actual = actual

class ValueError(Exception):
    def __init__(self, message):
        super().__init__(f"Value error: {message}")
        self.message = message

class NameError(Exception):
    def __init__(self, name):
        super().__init__(f"Name error: '{name}' is not defined")
        self.name = name

class IndexError(Exception):
    def __init__(self, message):
        super().__init__(f"Index error: {message}")
        self.message = message

class RuntimeError(Exception):
    def __init__(self, message):
        super().__init__(f"Runtime error: {message}")
        self.message = message

class TypeMismatchError(Exception):
    def __init__(self, expected, actual):
        super().__init__(f"Type mismatch: expected {expected}, got {actual}")
        self.expected = expected
        self.actual = actual

class VariableNotFoundError(Exception):
    def __init__(self, variable_name):
        super().__init__(f"Variable '{variable_name}' not found")
        self.variable_name = variable_name

class FunctionNotFoundError(Exception):
    def __init__(self, function_name):
        super().__init__(f"Function '{function_name}' not found")
        self.function_name = function_name

class InvalidArgumentError(Exception):
    def __init__(self, message):
        super().__init__(f"Invalid argument: {message}")

class RecursionLimitError(Exception):
    def __init__(self, function_name):
        super().__init__(f"Maximum recursion depth exceeded in function '{function_name}'")
        self.function_name = function_name

class DivisionByZeroError(Exception):
    def __init__(self):
        super().__init__("Division by zero")

class InvalidOperationError(Exception):
    def __init__(self, operation, types):
        super().__init__(f"Invalid operation: {operation} cannot be applied to {types}")
        self.operation = operation
        self.types = types

class InvalidVariableNameError(Exception):
    def __init__(self, name, reason="is a reserved keyword"):
        super().__init__(f"Invalid variable name: '{name}' {reason}")
        self.name = name
        self.reason = reason