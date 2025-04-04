# Description: Contains custom exceptions for the interpreter

# The system currently detects the following categories of errors:

# 1. Parsing and Syntax Errors:
#    - ParseError: For issues during code parsing with optional token information
#    - SyntaxWarning: Warnings about potentially problematic syntax
#    - UnknownTypeError: For unrecognized data types with suggestions for valid alternatives

# 2. Type and Name Errors:
#    - TypeError: For type mismatches
#    - NameError: For undefined variables/functions
#    - InvalidVariableNameError: For attempts to use reserved keywords as variables
#    - UndefinedVariableError: For variables referenced but not defined in scope
#    - RedeclarationError: For variables declared multiple times with different types

# 3. Runtime Errors:
#    - RuntimeError: General runtime issues
#    - ZeroDivisionError: For division by zero
#    - RecursionLimitError: For excessive recursion depth
#    - IndexError: For invalid array/list access
#    - ValueError: For invalid values in operations

# 4. Operation Errors:
#    - InvalidOperationError: For operations not allowed in specific contexts
#    - UndefinedBehaviorError: For operations with undefined behavior
#    - IncompatibleOperationError: For operations not supported by specific types

# 5. Resource and Memory Errors:
#    - StackError: For stack operation problems
#    - QueueOverflowError: For queue capacity exceeded
#    - StackOverflowError: For stack capacity exceeded
#    - EmptyStructureError: For operations on empty data structures
#    - MemoryError: For memory allocation/access issues
#    - ResourceWarning: For resource usage warnings

# 6. Module and Import Errors:
#    - ImportError: For problems importing modules

# 7. Concurrency and I/O Errors:
#    - ConcurrencyError: For issues in concurrent execution
#    - ConcurrentModificationError: For modifying structures during iteration
#    - IOError: For input/output operation failures

# 8. Data Structure Errors:
#    - TypeMismatchError: For type inconsistencies in structures
#    - InvalidAccessError: For improper access to data structures
#    - BoundaryError: For index out of range issues
#    - CircularReferenceError: For circular dependencies between structures
#    - StructureSizeError: For operations requiring specific structure sizes

# 9. Warning Types:
#    - DeprecationWarning: For use of deprecated features
#    - UnreachableCodeWarning: For code that will never execute
#    - ResourceWarning: For resource management issues

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

class EmptyStructureError(Exception):
    def __init__(self, structure_type, operation):
        super().__init__(f"Cannot perform '{operation}' on empty {structure_type}")

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

class RedeclarationError(Exception):
    def __init__(self, name):
        super().__init__(f"Redeclaration error: Variable '{name}' already declared with a different type")

class StackOverflowError(Exception):
    def __init__(self, stack_name, limit):
        super().__init__(f"Stack overflow in '{stack_name}': Exceeded maximum capacity of {limit} elements")

class QueueOverflowError(Exception):
    def __init__(self, queue_name, limit):
        super().__init__(f"Queue overflow in '{queue_name}': Exceeded maximum capacity of {limit} elements")

class TypeMismatchError(Exception):
    def __init__(self, structure_name, expected_type, provided_type):
        super().__init__(f"Type mismatch in '{structure_name}': Expected {expected_type}, got {provided_type}")

class InvalidAccessError(Exception):
    def __init__(self, structure_name, operation, reason):
        super().__init__(f"Invalid access to '{structure_name}' during {operation}: {reason}")

class BoundaryError(Exception):
    def __init__(self, index, min_val, max_val):
        super().__init__(f"Boundary error: Index {index} outside valid range [{min_val}, {max_val}]")

class CircularReferenceError(Exception):
    def __init__(self, structure_names):
        super().__init__(f"Circular reference detected between: {', '.join(structure_names)}")

class StructureSizeError(Exception):
    def __init__(self, structure_name, operation, required_size, actual_size):
        super().__init__(f"Size error for '{structure_name}' during {operation}: Required at least {required_size} elements, but has {actual_size}")

class ConcurrentModificationError(Exception):
    def __init__(self, structure_name):
        super().__init__(f"Concurrent modification detected in '{structure_name}': Structure was modified during iteration")

class IncompatibleOperationError(Exception):
    def __init__(self, operation, structure_type):
        super().__init__(f"Operation '{operation}' is not supported for {structure_type} type")

class UndefinedVariableError(Exception):
    def __init__(self, var_name):
        super().__init__(f"Undefined variable: '{var_name}' is not defined in the current scope")

class UnknownTypeError(Exception):
    def __init__(self, unknown_type, suggested_types=None):
        error_msg = f"Unknown data type: '{unknown_type}'"
        if suggested_types:
            suggestions = ", ".join(f"'{t}'" for t in suggested_types[:3])
            error_msg += f". Valid types include: {suggestions}"
        super().__init__(error_msg)

class UndefinedTypeError(Exception):
    def __init__(self, type_name, suggestions=None):
        error_msg = f"Undefined type: '{type_name}'"
        if suggestions:
            similar = suggestions[0] if suggestions else None
            if similar:
                error_msg += f" - did you mean '{similar}'?"
            else:
                valid_types = ", ".join(f"'{t}'" for t in list(suggestions)[:3])
                error_msg += f". Valid types include: {valid_types}"
        super().__init__(error_msg)

# Update the handle_error function to be more concise
def handle_error(error, stop_execution=True):
    """
    Central error handling function.
    Displays the error message and optionally stops program execution.
    
    Args:
        error: The exception that was raised
        stop_execution: If True, exits the program after displaying the error
    """
    # Check if running in terminal that supports ANSI colors
    try:
        import os
        is_terminal = os.isatty(1)  # Check if stdout is a terminal
        use_color = is_terminal
    except:
        use_color = False
    
    # Format error message
    if use_color:
        error_msg = f"\033[91mERROR: {error}\033[0m"  # Red text
    else:
        error_msg = f"ERROR: {error}"
    
    print(error_msg)
    
    if stop_execution:
        import sys
        sys.exit(1)  # Exit with error code instead of raising exception

# Add error reporting class that inherits from all exceptions
class CompilerError(Exception):
    """Base class for all compiler errors that should stop execution"""
    def __init__(self, message):
        self.message = message
        super().__init__(message)
        handle_error(self)