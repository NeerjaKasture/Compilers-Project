# Description: Contains custom exceptions for the interpreter

class ParseError(Exception):
    def __init__(self, msg, token=None):
        self.msg = msg
        self.token = token
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Parse error: {msg}{line_info}")

class NameError(Exception):
    def __init__(self, name, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Name error: {name}{line_info}")

class InvalidVariableNameError(Exception):
    def __init__(self, name, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Invalid variable name: '{name}' is a reserved keyword{line_info}")

class InvalidOperationError(Exception):
    def __init__(self, op, context, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Invalid operation: {op} in {context} context{line_info}")

class ZeroDivisionError(Exception):
    def __init__(self, msg="Division by zero", token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"{msg}{line_info}")

class RuntimeError(Exception):
    def __init__(self, msg, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Runtime error: {msg}{line_info}")

class RecursionLimitError(Exception):
    def __init__(self, function_name, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Maximum recursion depth exceeded in function '{function_name}'{line_info}")

class StackError(Exception):
    def __init__(self, operation, msg, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Stack error during '{operation}': {msg}{line_info}")

class ImportError(Exception):
    def __init__(self, module_name, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Could not import module: '{module_name}'{line_info}")

class UndefinedBehaviorError(Exception):
    def __init__(self, operation, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Undefined behavior detected in operation: {operation}{line_info}")

class MemoryError(Exception):
    def __init__(self, operation, msg, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"Memory error during '{operation}': {msg}{line_info}")

class IOError(Exception):
    def __init__(self, operation, msg, token=None):
        line_info = f" on line {token.line}" if token and hasattr(token, 'line') else ""
        super().__init__(f"I/O error during '{operation}': {msg}{line_info}")

class SyntaxWarning(Warning):
    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line
        super().__init__(f"Syntax warning: {msg}" + (f" at line {line}" if line else ""))
