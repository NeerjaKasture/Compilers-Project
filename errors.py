# Description: Contains custom exceptions for the interpreter

class ParseError(Exception):
    def __init__(self, msg, token=None):
        self.msg = msg
        self.token = token
        super().__init__(f"Parse error: {msg}" + (f" at {token}" if token else ""))

class TypeError(Exception):
    def __init__(self, expected, got):
        super().__init__(f"Type error: Expected {expected}, got {got}")

class NameError(Exception):
    def __init__(self, name):
        super().__init__(f"Name error: {name}")

class InvalidVariableNameError(Exception):
    def __init__(self, name):
        super().__init__(f"Invalid variable name: '{name}' is a reserved keyword")

class InvalidOperationError(Exception):
    def __init__(self, op, context):
        super().__init__(f"Invalid operation: {op} in {context} context")

class ZeroDivisionError(Exception):
    def __init__(self, msg="Division by zero"):
        super().__init__(msg)

class RuntimeError(Exception):
    def __init__(self, msg):
        super().__init__(f"Runtime error: {msg}")

class RecursionLimitError(Exception):
    def __init__(self, function_name):
        super().__init__(f"Maximum recursion depth exceeded in function '{function_name}'")

class IndexError(Exception):
    def __init__(self, msg):
        super().__init__(f"Index error: {msg}")

class ValueError(Exception):
    def __init__(self, msg):
        super().__init__(f"Value error: {msg}")

# New error types

class StackError(Exception):
    def __init__(self, operation, msg):
        super().__init__(f"Stack error during '{operation}': {msg}")

class ImportError(Exception):
    def __init__(self, module_name):
        super().__init__(f"Could not import module: '{module_name}'")

class UndefinedBehaviorError(Exception):
    def __init__(self, operation):
        super().__init__(f"Undefined behavior detected in operation: {operation}")

class ConcurrencyError(Exception):
    def __init__(self, msg):
        super().__init__(f"Concurrency error: {msg}")

class MemoryError(Exception):
    def __init__(self, operation, msg):
        super().__init__(f"Memory error during '{operation}': {msg}")

class IOError(Exception):
    def __init__(self, operation, msg):
        super().__init__(f"I/O error during '{operation}': {msg}")

class SyntaxWarning(Warning):
    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line
        super().__init__(f"Syntax warning: {msg}" + (f" at line {line}" if line else ""))

class DeprecationWarning(Warning):
    def __init__(self, feature, alternative=None):
        msg = f"'{feature}' is deprecated"
        if alternative:
            msg += f", use '{alternative}' instead"
        super().__init__(msg)

class UnreachableCodeWarning(Warning):
    def __init__(self, line=None):
        super().__init__(f"Unreachable code detected" + (f" at line {line}" if line else ""))

class ResourceWarning(Warning):
    def __init__(self, resource, msg):
        super().__init__(f"Resource '{resource}' warning: {msg}")