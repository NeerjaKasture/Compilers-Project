from dataclasses import dataclass, field
from collections.abc import Iterator
from more_itertools import peekable
import sys
from typing import Optional, List

# Base class for all AST nodes
class AST:
    pass

# AST node for binary operations
@dataclass
class BinOp(AST):
    op: str
    left: AST
    right: AST|None

# AST node for a sequence of statements
class Sequence(AST):
    __match_args__ = ("statements",)  # Tells Python to expect a "statements" attribute during matching

    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Sequence({self.statements})"

# AST node for conditional statements
@dataclass
class Cond(AST):
    If: tuple[AST, AST]  # ('condition', 'body') for the 'if' statement
    Elif: Optional[List[tuple[AST, AST]]] # Optional list of ('condition', 'body') for each 'elif'
    Else: Optional[AST] = None 
    
# AST node for while loops
@dataclass
class While(AST):
    condition: AST
    body: list[AST]  

@dataclass
class For(AST):
    init: AST
    condition: AST
    increment: AST
    body: list[AST]

# AST node for numbers
@dataclass
class Number(AST):
    val: str

# AST node for parenthesis expressions
@dataclass
class Parenthesis(AST):
    expr: AST

@dataclass
class SemicolonToken(AST):
    s: str

# AST node for boolean values
@dataclass
class Boolean(AST):
    val: str

# AST node for string values
@dataclass
class String(AST):
    val: str

# AST node for variables
@dataclass
class Variable(AST):
    val: str

# AST node for variable declarations
@dataclass
class Declaration(AST):
    type: str
    name: str
    value: AST

# AST node for variable assignments
@dataclass
class Assignment(AST):
    name: str
    value: AST

# AST node for string concatenation
@dataclass
class Concat(AST):
    left: str
    right: str 

@dataclass
class Function(AST):
    name: str
    params: list[tuple[str, str]]  # List of (type, name) pairs
    return_type: str
    body: AST  

@dataclass
class FunctionCall(AST):
    name: str
    params: list[str] 
      
@dataclass
class Return(AST):
    value: AST

# Update the Print AST node to handle multiple values
@dataclass
class Print(AST):
    values: list[AST]  # Changed from single value to list of values

@dataclass
class Array(AST):
    elements: list[AST]

@dataclass
class ArrayAccess(AST):
    array: AST
    index: AST

@dataclass
class ArrayAssignment(AST):
    array: AST
    index: AST
    value: AST

@dataclass
class Input(AST):
    type: str  

# Dictionary to map data types to Python types
datatypes = {
    "int": int, 
    "float": float, 
    "bool": bool, 
    "string": str,
    "int[]": list,
    "float[]": list,
    "bool[]": list,
    "string[]": list
}

def is_array_type(type_str: str) -> bool:
    return type_str.endswith('[]')

def get_base_type(type_str: str) -> str:
    return type_str[:-2] if is_array_type(type_str) else type_str

# Function to evaluate the AST
def e(tree: AST, env={}, types={}): # could also make the env dict global 
    match tree:
        case Input(type):
            try:
                user_input = input()
                match type:
                    case "int":
                        return int(user_input)
                    case "float":
                        return float(user_input)
                    case "string":
                        return str(user_input)
                    case _:
                        raise TypeError(f"Unsupported input type: {type}")
            except ValueError as ve:
                print(f"Invalid input for type {type}: {ve}")
                return None
        case Variable(v):
            if v in env:
                return env[v]
            else:
                raise NameError(f"Undefined variable: {v}")

        case Function(name, params, return_type, body):  
            env[name] = tree  
            return None  

        case FunctionCall(name, args):
            if name not in env or not isinstance(env[name], Function):
                raise NameError(f"Undefined function: {name}")

            func = env[name]
            if len(args) != len(func.params):
                raise TypeError(f"Function '{name}' expects {len(func.params)} arguments but got {len(args)}")

            # This means that all var in env are global and accessible by function to read only
            local_env = env.copy()
            local_types = types.copy()

            # Bind function arguments
            for (param_type, param_name), arg in zip(func.params, args):
                arg_value = e(arg, env, types)

                if not isinstance(arg_value, datatypes[param_type]):
                    raise TypeError(f"Argument '{param_name}' must be of type {param_type}")

                local_env[param_name] = arg_value
                local_types[param_name] = param_type
            
            result = e(func.body, local_env, local_types)
        
            if func.return_type != "void" and not isinstance(result, datatypes[func.return_type]):
                raise TypeError(f"Function '{name}' must return a value of type {func.return_type}, but got {type(result).__name__}")

            return result
        
        case Return(expr):
            return e(expr, env, types)

        case Boolean(v):
            if v == "true":
                return True # how would we make our compiler evaluate 'true' as True but still return true as output
            else:
                return False
        case Parenthesis(expr):
            return e(expr)
        case Number(v):
            if '.' in v:
                return float(v)
            else:
                return int(v)
        case BinOp(op, l, r):
            if isinstance(e(l), bool) or isinstance(e(r), bool):
                if op in {"+", "-", "*", "/", "^","<",">","<=",">="}:
                    raise TypeError(f"Cannot apply '{op}' to Boolean type")
                match op:
                    case "and":
                        return e(l) and e(r)
                    case "or":
                        return e(l) or e(r)
                    case "not":
                        return not e(l)
            if isinstance(e(l), str) or isinstance(e(r), str):
                if op in {"+", "-", "*", "/", "^","<",">","<=",">="}:
                    raise TypeError(f"Cannot apply '{op}' to String type")  
            match op:
                case "+":
                    return e(l) + e(r)
                case "-":
                    return e(l) - e(r)
                case "*":
                    return e(l) * e(r)
                case "/":
                    if e(r) == 0:
                        raise ZeroDivisionError("Division by zero")
                    return e(l) / e(r)
                case "^":
                    return e(l) ** e(r)
                case "<":
                    return e(l) < e(r)
                case ">":
                    return e(l) > e(r)
                case "==":
                    return e(l) == e(r)
                case "!=":
                    return e(l) != e(r)
        case Cond(If, Elif, Else):
            if e(If[0]):
                return e(If[1])  # Execute the 'If' body

            # If there are any 'elif' conditions, check each one
            if Elif:  # Check if Elif is not empty
                for elif_condition, elif_body in Elif:
                    if e(elif_condition):  # Evaluating 'elif' condition
                        return e(elif_body)  # Execute the corresponding 'elif' body

            # If no condition matched, check 'Else' (if exists)
            if Else is not None:
                return e(Else)  # Execute the 'Else' body

            # Default return value if no conditions matched
            return None
        
        case Declaration(var_type, var_name, value):
            val = e(value, env, types)
            if val is None:  # Handle failed input
                raise ValueError(f"Failed to get valid input for {var_name}")
            if is_array_type(var_type):
                if not isinstance(val, list):
                    raise TypeError(f"Variable '{var_name}' must be of type {var_type}")
                # Check that all elements are of the base type
                base_type = datatypes[get_base_type(var_type)]
                if not all(isinstance(x, base_type) for x in val):
                    raise TypeError(f"All elements in array '{var_name}' must be of type {get_base_type(var_type)}")
            elif not isinstance(val, datatypes[var_type]):
                raise TypeError(f"Variable '{var_name}' must be of type {var_type}")

            env[var_name] = val

            # is this ok to store type of python itself and not a string?
            types[var_name] = var_type


            return val
        
        case Assignment(var_name, value):
            if var_name not in env:
                raise NameError(f"Undefined variable: {var_name}")

            val = e(value, env, types)

            if not isinstance(val, datatypes[types[var_name]]):
                raise TypeError(f"Variable '{var_name}' must be of type {types[var_name]}")

            env[var_name] = val
            return val
        
        case While(condition, body):
            while e(condition, env, types):
                if isinstance(body, Sequence):
                    for stmt in body.statements:
                        result = e(stmt, env, types)
                        if result is not None:
                            print(result)
                else:
                    result = e(body, env, types)
                    if result is not None:
                        print(result)
            return None
        
        case For(init, condition, increment, body):
            xy = None
            e(init, env, types)  # Execute initialization (e.g., i = 0)
            while e(condition, env, types):  # Check loop condition
                if isinstance(body, Sequence):
                    for stmt in body.statements:
                        xy = e(stmt, env, types)  # Execute loop body
                        if xy is not None:
                            print(xy)
                else:
                    xy = e(body, env, types)
                    if xy is not None:
                        print(xy)
                e(increment, env, types)  # Execute increment (e.g., i = i + 1)
            return xy

        case Sequence(statements):
            last_value = []
            for stmt in statements:
                last_value.append(e(stmt, env, types))  # Evaluate each statement
            return last_value
        case String(v):
            return v
        case Concat(left, right):
            left_val = e(left, env, types)
            right_val = e(right, env, types)

            if not isinstance(left_val, str) or not isinstance(right_val, str):
                raise TypeError("Concat can only be used with String")

            return left_val + right_val 
        case Print(values):
            results = []
            for value in values:
                result = e(value, env, types)
                results.append(result)
            print(*results)  # This will print the values
            return None
            # results = [e(value, env, types) for value in values]
            # print(*results)  # Changed to use default print behavior with newline
            # return None
        case Array(elements):
            return [e(element, env, types) for element in elements]
        case ArrayAccess(array, index):
            array_val = e(array, env, types)
            index_val = e(index, env, types)
            if not isinstance(array_val, list):
                raise TypeError("Array access can only be used with arrays")
            return array_val[index_val]
        case ArrayAssignment(array, index, value):
            array_val = e(array, env, types)
            index_val = e(index, env, types)
            value_val = e(value, env, types)
            if not isinstance(array_val, list):
                raise TypeError("Array assignment can only be used with arrays")
            array_val[index_val] = value_val
            return value_val

# Base class for all tokens
class Token:
    pass

# Token classes for different types of tokens
@dataclass
class NumberToken(Token):
    n: str

@dataclass
class ParenthesisToken(Token):
    p: str

@dataclass
class KeywordToken(Token):
    value: str

@dataclass
class OperatorToken(Token):
    o: str

@dataclass
class BooleanToken(Token):
    b: str

@dataclass
class StringToken(Token):
    s: str

@dataclass
class VariableToken(Token):
    v: str

@dataclass
class TypeToken(Token):
    t: str

@dataclass
class SymbolToken(Token):
    s: str

# Set of keywords
keywords = {"if", "elif", "else", "true", "false", "print", "concat", "while", "for", "and", "or", "not", "def", "return", "void"}

class ParseError(Exception):
    def __init__(self, message, token):
        super().__init__(f"Error at token {token}: {message}")
        self.token = token

# Lexer function to tokenize the input string
def lex(s: str) -> Iterator[Token]:
    i = 0
    while i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1

        if i >= len(s):
            return

        if s[i].isalpha():
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                i += 1
            word = s[start:i]
            if word in datatypes.keys():
                yield TypeToken(word)
            elif word in keywords:
                if word in ["true", "false"]:
                    yield BooleanToken(word)
                elif word in ["and", "or", "not"]:
                    yield OperatorToken(word)
                else:
                    yield KeywordToken(word)
            else:
                yield VariableToken(word)

        elif s[i].isdigit():
            t = s[i]
            i += 1
            has_decimal = False
            while i < len(s) and (s[i].isdigit() or (s[i] == '.' and not has_decimal)):
                if s[i] == '.':
                    has_decimal = True
                t += s[i]
                i += 1
            yield NumberToken(t)

        elif s[i] == '"':
            i += 1
            start = i
            while i < len(s) and s[i] != '"':
                i += 1
            yield StringToken(s[start:i])
            i += 1

        else:
            match s[i]:
                case '+' | '*' | '-' | '/' | '^' | '(' | ')' | '<' | '>' | '=' | '!' | '~' | '{' | '}' | ';' | ',' | '[' | ']' | '->':
                    if s[i] in '<>=!' and i + 1 < len(s) and s[i + 1] == '=':
                        yield OperatorToken(s[i:i + 2])
                        i += 2
                    else:
                        if s[i] in "}(){[]":
                            yield ParenthesisToken(s[i])
                        elif s[i] == '-' and i + 1 < len(s) and s[i + 1] == '>':
                            yield SymbolToken('->')
                            i += 2
                        elif s[i] in '+ * - / ^ ~><=':
                            yield OperatorToken(s[i])
                        else:
                            yield SymbolToken(s[i])
                        i += 1
                case _:
                    raise ParseError(f"Unexpected character: {s[i]}", s[i])

# Parser function to parse the tokenized input
def parse(s: str) -> AST:
    t = peekable(lex(s))

    def parse_sequence(inside_function=False):
        statements = []
        while True:
            try:
                match t.peek(None):
                    case KeywordToken("def"):  # Function definition
                        statements.append(parse_function())
                    case KeywordToken("return"):
                        if not inside_function:
                            raise ParseError("Return statement outside Function body", t.peek())
                        next(t)
                        expr = parse_comparator()
                        statements.append(Return(expr))

                        if t.peek(None) == SymbolToken(";"):
                            next(t)
                        else:
                            raise ParseError("Expected ';' after return statement", t.peek())
                    case KeywordToken("print"):
                        next(t)  # Consume 'print'
                        if t.peek(None) != ParenthesisToken("("):
                            raise ParseError("Expected '(' after print keyword", t.peek())
                        next(t)  # Consume '('
                        
                        values = []
                        while t.peek(None) and not isinstance(t.peek(None), ParenthesisToken):
                            if isinstance(t.peek(None), VariableToken):
                                var_name = next(t).v
                                if t.peek(None) == ParenthesisToken('['):
                                    # Handle array access
                                    next(t)  # Consume '['
                                    index = parse_comparator()
                                    if next(t) != ParenthesisToken(']'):
                                        raise ParseError("Expected ']' after array index", t.peek())
                                    values.append(ArrayAccess(Variable(var_name), index))
                                else:
                                    t.prepend(VariableToken(var_name))
                                    values.append(parse_comparator())
                            else:
                                values.append(parse_comparator())
                                
                            if t.peek(None) == SymbolToken(","):
                                next(t)
                            else:
                                break
                                
                        if next(t) != ParenthesisToken(")"):
                            raise ParseError("Expected ')' after print arguments", t.peek())
                            
                        statements.append(Print(values))
                        
                        if t.peek(None) == SymbolToken(";"):
                            next(t)
                        else:
                            raise ParseError("Expected ';' after print statement", t.peek())
                    case ParenthesisToken('}'):
                        next(t)  # Consume '}'
                        break  # End of block
                    case _:
                        stmt = parse_condition()
                        statements.append(stmt)

                match t.peek(None):
                    case SymbolToken(';'):
                        next(t)
                    case _:
                        break
            except ParseError as e:
                print(e)
                break
        return Sequence(statements) if len(statements) > 1 else statements[0]

    def parse_function_call():
        try:
            match t.peek(None):
                case VariableToken(name):
                    next(t)  # Consume function name

                    if next(t) != ParenthesisToken("("):
                        raise ParseError("Expected '(' after function name", t.peek())

                    args = []
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).p == ")"):
                        args.append(parse_comparator())

                        if t.peek(None) == SymbolToken(","):
                            next(t)
                        else:
                            break

                    if next(t) != ParenthesisToken(")"):
                        raise ParseError("Expected ')' after function arguments", t.peek())

                    return FunctionCall(name, args)
                case _:
                    raise ParseError("Expected function name for function call", t.peek())
        except ParseError as e:
            print(e)
            return None

    def parse_function():
        try:
            match t.peek(None):
                case KeywordToken("def"):  # Function return type
                    next(t)
                    match t.peek(None):
                        case VariableToken(name):
                            next(t)
                            if next(t) != ParenthesisToken("("):
                                raise ParseError("Expected '(' after function name", t.peek())
                            params = []

                            while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).p == ")"):
                                param_type_token = next(t)

                                if not isinstance(param_type_token, TypeToken):
                                    raise ParseError(f"Expected a type for function parameter, got {param_type_token}", t.peek())

                                param_type = param_type_token.t

                                param_name_token = next(t)

                                if not isinstance(param_name_token, VariableToken):
                                    raise ParseError(f"Expected a variable name, got {param_name_token}", t.peek())

                                param_name = param_name_token.v

                                params.append((param_type, param_name))

                                if t.peek(None) == SymbolToken(","):
                                    next(t)
                                else:
                                    break
                            if next(t) != ParenthesisToken(")"):
                                raise ParseError("Expected ')' after function parameters", t.peek())

                            if t.peek(None) == SymbolToken("->"):
                                next(t)
                                if not isinstance(t.peek(None), TypeToken):
                                    raise ParseError("Expected return type after '->'", t.peek())
                                return_type = next(t).t
                            else:
                                return_type = 'void'

                            if next(t) != ParenthesisToken("{"):
                                raise ParseError("Expected { before function body", t.peek())

                            body = parse_sequence(inside_function=True)

                            if next(t) != ParenthesisToken("}"):
                                raise ParseError("Expected } after function body", t.peek())

                            return Function(name, params, return_type, body)
                        case _:
                            raise ParseError("Expected function name after 'def'", t.peek())
        except ParseError as e:
            print(e)
            return None

    def parse_condition():
        try:
            match t.peek(None):
                case KeywordToken('if'):
                    next(t)  # Consume 'if'

                    # Parse the condition inside parentheses
                    if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != '(':
                        raise ParseError("Expected '(' after 'if' keyword", t.peek())

                    next(t)  # Consume '('
                    condition = parse_comparator()

                    closing_paren = next(t, None)  # Consume next token
                    if not isinstance(closing_paren, ParenthesisToken) or closing_paren.p != ')':
                        raise ParseError("Expected ')' after if condition", t.peek())

                    # Parse the if body inside curly brackets
                    if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != '{':
                        raise ParseError("Expected '{' after if condition", t.peek())

                    next(t)  # Consume '{'
                    if_branch = parse_sequence()  # Single expression
                    if t.peek(None) != ParenthesisToken('}'):
                        raise ParseError("Expected '}' after if body", t.peek())
                    next(t)  # Consume '}'

                    # Parse multiple elif branches
                    elif_branches = []
                    while isinstance(t.peek(None), KeywordToken) and t.peek(None).value == 'elif':
                        next(t)  # Consume 'elif'

                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != '(':
                            raise ParseError("Expected '(' after elif keyword", t.peek())

                        next(t)  # Consume '('
                        elif_condition = parse_comparator()

                        closing_paren = next(t, None)  # Consume next token
                        if not isinstance(closing_paren, ParenthesisToken) or closing_paren.p != ')':
                            raise ParseError("Expected ')' after elif condition", t.peek())

                        # Parse elif body
                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != '{':
                            raise ParseError("Expected '{' after elif condition", t.peek())

                        next(t)  # Consume '{'
                        elif_body = parse_sequence()  # Single expression
                        if t.peek(None) != ParenthesisToken('}'):
                            raise ParseError("Expected '}' after elif body", t.peek())
                        next(t)  # Consume '}'

                        elif_branches.append((elif_condition, elif_body))

                    # Parse optional else block
                    else_branch = None
                    if isinstance(t.peek(None), KeywordToken) and t.peek(None).value == 'else':
                        next(t)  # Consume 'else'

                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != '{':
                            raise ParseError("Expected '{' after else keyword", t.peek())

                        next(t)  # Consume '{'
                        else_branch = parse_sequence()  # Single expression
                        if t.peek(None) != ParenthesisToken('}'):
                            raise ParseError("Expected '}' after else body", t.peek())
                        next(t)  # Consume '}'

                    return Cond((condition, if_branch), elif_branches, else_branch)

                case KeywordToken('for'):
                    next(t)
                    match t.peek(None):
                        case ParenthesisToken('('):
                            next(t)
                            init = parse_assignment()  # Parse initialization (e.g., int i = 0)

                            match next(t, None):
                                case SymbolToken(';'):
                                    pass
                                case _:
                                    raise ParseError("Expected ';' after for-loop initialization", t.peek())

                            condition = parse_comparator()  # Parse condition (e.g., i < 10)

                            match next(t, None):
                                case SymbolToken(';'):
                                    pass
                                case _:
                                    raise ParseError("Expected ';' after for-loop condition", t.peek())

                            increment = parse_assignment()  # Parse increment (e.g., i = i + 1)

                            match next(t, None):
                                case ParenthesisToken(')'):
                                    pass
                                case _:
                                    raise ParseError("Expected ')' after for-loop increment", t.peek())

                        case _:
                            raise ParseError("Expected '(' after 'for' keyword", t.peek())

                    match t.peek(None):
                        case ParenthesisToken('{'):
                            next(t)
                            body = parse_sequence()  # Parse the body of the for loop
                            if t.peek(None) != ParenthesisToken('}'):
                                raise ParseError("Expected '}' after for-loop body", t.peek())
                            next(t)  # Consume '}'
                            return For(init, condition, increment, body)

                        case _:
                            raise ParseError("Expected '{' after for-loop definition", t.peek())

                case KeywordToken('while'):
                    next(t)
                    match t.peek(None):
                        case ParenthesisToken('('):
                            next(t)
                            condition = parse_comparator()
                            match next(t, None):
                                case ParenthesisToken(')'):
                                    pass
                                case _:
                                    raise ParseError("Expected ')' after while condition", t.peek())
                        case _:
                            raise ParseError("Expected '(' after 'while' keyword", t.peek())
                    match t.peek(None):
                        case ParenthesisToken('{'):
                            next(t)
                            body = parse_sequence()  # Parse the body of the while loop
                            if t.peek(None) != ParenthesisToken('}'):
                                raise ParseError("Expected '}' after while-loop body", t.peek())
                            next(t)  # Consume '}'
                            return While(condition, body)
                        case _:
                            raise ParseError("Expected '{' after while condition", t.peek())
                case _:
                    return parse_assignment()
        except ParseError as e:
            print(e)
            return None

    def parse_assignment():
        try:
            match t.peek(None):
                case VariableToken(var_name):
                    next(t)
                    match t.peek(None):
                        case OperatorToken('='):  # assignment
                            next(t)
                            value = parse_comparator()
                            return Assignment(var_name, value)
                        case ParenthesisToken('('):  # Function call
                            t.prepend(VariableToken(var_name))
                            return parse_function_call()
                        case ParenthesisToken('['):  # Array access or assignment
                            next(t)
                            index = parse_comparator()
                            if next(t) != ParenthesisToken(']'):
                                raise ParseError("Expected ']' after array index", t.peek())
                            if t.peek(None) == OperatorToken('='):
                                next(t)
                                value = parse_comparator()
                                return ArrayAssignment(Variable(var_name), index, value)
                            return ArrayAccess(Variable(var_name), index)
                        case _:
                            t.prepend(VariableToken(var_name))  # Put back the variable token
                            return parse_comparator()
                case _:
                    return parse_declaration()
        except ParseError as e:
            print(e)
            return None

    def parse_declaration():
        try:
            match t.peek(None):
                case TypeToken(var_type):
                    if var_type not in datatypes.keys():
                        raise ParseError(f"Invalid type: {var_type}", t.peek())
                    else:
                        next(t)
                        match t.peek(None):
                            case VariableToken(var_name):
                                if var_name in keywords:
                                    raise ParseError(f"Invalid variable name: {var_name}", t.peek())
                                else:
                                    next(t)
                                    match t.peek(None):
                                        case OperatorToken('='):
                                            next(t)
                                            if isinstance(t.peek(None), VariableToken) and t.peek(None).v == "input":
                                                next(t)  # consume 'input'
                                                if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != '(':
                                                    raise ParseError("Expected '(' after input", t.peek())
                                                next(t)
                                                if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).p != ')':
                                                    raise ParseError("Expected ')' after input", t.peek())
                                                next(t) 
                                                return Declaration(var_type, var_name, Input(var_type))
                                            value = parse_comparator()
                                            return Declaration(var_type, var_name, value)
                                        case ParenthesisToken('['):  # Array declaration
                                            next(t)
                                            elements = []
                                            while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).p == "]"):
                                                elements.append(parse_comparator())
                                                if t.peek(None) == SymbolToken(","):
                                                    next(t)
                                                else:
                                                    break
                                            if next(t) != ParenthesisToken("]"):
                                                raise ParseError("Expected ']' after array elements", t.peek())
                                            return Declaration(var_type + "[]", var_name, Array(elements))
                                        case _:
                                            raise ParseError("Expected '=' or '[' after variable name", t.peek())
                            case ParenthesisToken('['):  # Array type
                                next(t)
                                if next(t) != ParenthesisToken(']'):
                                    raise ParseError("Expected ']' after '[' in array type", t.peek())
                                match t.peek(None):
                                    case VariableToken(var_name):
                                        if var_name in keywords:
                                            raise ParseError(f"Invalid variable name: {var_name}", t.peek())
                                        else:
                                            next(t)
                                            match t.peek(None):
                                                case OperatorToken('='):
                                                    next(t)
                                                    value = parse_comparator()
                                                    return Declaration(var_type + "[]", var_name, value)
                                                case _:
                                                    raise ParseError("Expected '=' after array variable name", t.peek())
                                    case _:
                                        raise ParseError("Expected variable name after array type", t.peek())
                            case _:
                                raise ParseError("Expected variable name or '[' after type", t.peek())
                case _:
                    return parse_comparator()
        except ParseError as e:
            print(e)
            return None

    def parse_comparator():
        try:
            ast = parse_add()
            while True:
                match t.peek(None):
                    case OperatorToken(op):
                        if op in {"<", ">", "==", "!="}:
                            next(t)
                            ast = BinOp(op, ast, parse_add())
                        elif op in {"and", "or"}:
                            next(t)
                            ast = BinOp(op, ast, parse_add())
                        elif op in {"not"}:
                            next(t)
                            ast = BinOp(op, ast, parse_add())
                        else:
                            raise ParseError("Unexpected operator", t.peek())
                    case _:
                        return ast
        except ParseError as e:
            print(e)
            return None

    def parse_add():
        try:
            ast = parse_sub()
            while True:
                match t.peek(None):
                    case OperatorToken('+'):
                        next(t)
                        ast = BinOp('+', ast, parse_sub())
                    case _:
                        return ast
        except ParseError as e:
            print(e)
            return None

    def parse_sub():
        try:
            ast = parse_mul()
            while True:
                match t.peek(None):
                    case OperatorToken('-'):
                        next(t)
                        ast = BinOp('-', ast, parse_mul())
                    case _:
                        return ast
        except ParseError as e:
            print(e)
            return None

    def parse_mul():
        try:
            ast = parse_div()
            while True:
                match t.peek(None):
                    case OperatorToken('*'):
                        next(t)
                        ast = BinOp('*', ast, parse_div())
                    case _:
                        return ast
        except ParseError as e:
            print(e)
            return None

    def parse_div():
        try:
            ast = parse_exponent()
            while True:
                match t.peek(None):
                    case OperatorToken('/'):
                        next(t)
                        divisor = parse_exponent()
                        ast = BinOp('/', ast, divisor)
                    case _:
                        return ast
        except ParseError as e:
            print(e)
            return None

    def parse_exponent():
        try:
            ast = parse_atom()
            while True:
                match t.peek(None):
                    case OperatorToken('^'):
                        next(t)
                        ast = BinOp('^', ast, parse_exponent())
                    case _:
                        return ast
        except ParseError as e:
            print(e)
            return None

    def parse_atom():
        try:
            match t.peek(None):
                case KeywordToken('concat'):
                    next(t)
                    match t.peek(None):
                        case ParenthesisToken('('):
                            next(t)
                            left = parse_atom()
                            match t.peek(None):
                                case OperatorToken(','):
                                    next(t)
                                    right = parse_atom()
                                    match t.peek(None):
                                        case ParenthesisToken(')'):
                                            next(t)
                                            return Concat(left, right)
                                        case _:
                                            raise ParseError("Expected ')' after concat arguments", t.peek())
                                case _:
                                    raise ParseError("Expected ',' after first concat argument", t.peek())
                        case _:
                            raise ParseError("Expected '(' after 'concat'", t.peek())
                case OperatorToken('~'):  # Check for the tilde operator
                    next(t)
                    return BinOp('*', Number('-1'), parse_atom())
                case VariableToken(v):
                    next(t)
                    return Variable(v)
                case NumberToken(v):
                    next(t)
                    return Number(v)
                case BooleanToken(v):
                    next(t)
                    return Boolean(v)
                case ParenthesisToken('('):
                    next(t)
                    expr = parse_comparator()
                    match next(t, None):
                        case ParenthesisToken(')'):
                            return Parenthesis(expr)
                        case _:
                            raise ParseError("Expected ')' after expression", t.peek())
                case StringToken(v):
                    next(t)
                    return String(v)
                case ParenthesisToken('['):
                    next(t)
                    elements = []
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).p == "]"):
                        elements.append(parse_comparator())
                        if t.peek(None) == SymbolToken(","):
                            next(t)
                        else:
                            break
                    if next(t) != ParenthesisToken("]"):
                        raise ParseError("Expected ']' after array elements", t.peek())
                    return Array(elements)
                case _:
                    raise ParseError(f"Unexpected token: {t.peek(None)}", t.peek())
        except ParseError as e:
            print(e)
            return None

    return parse_sequence()

def run_test(code):
    try:
        print(f"\nExecuting: {code}")
        ast = parse(code)
        if ast is None:
            print("Failed to parse the code")
            return
        e(ast)  # Just execute, don't print result
    except Exception as ex:
        print(f"Error: {ex}\n")

print("\n=== Input Tests ===")
run_test("int siri = input(); print(siri*2);")
run_test("float har = input(); print(har);")
run_test("string aks = input(); print(aks);")
# Test cases with added print title separators
print("\n=== Basic Tests ===")
print(e(parse("print(5+3);"))) 
print(e(parse('print("Mom and Dad");')))  
print(e(parse('print("HI");')))
print(e(parse("int x=12; print(x);")))

print("\n=== Conditional Tests ===")
print(e(parse("int x=12; int y=2; if (x < 4) { x=10; y=2} elif (x < 8 ) { x=20; y=30} elif (x < 10) { x=40; y=60} else { x=15; y=45}; print(y);")))

print("\n=== Loop Tests ===")
run_test("for (int i=0; i<3; i=i+1) {print(i);}")
run_test("int i=0; while (i < 3) { print(i); i = i + 1; }")

print("\n=== Array Tests ===")
print(e(parse('print("array test cases");')))
run_test("int[] arr = [1, 2, 3]; print(arr[2]);")
print(e(parse('print("new case");')))
run_test("int[] arr = [1, 2, 3]; arr[1] = 10; print(arr[0], arr[1], arr[2]);")

print("\n=== Expression Tests ===")
run_test("int a=5; int b=10; print(a + b);")
run_test("int a=5; int b=10; print(a * b);")
run_test("int a=5; int b=10; print(a < b);")
run_test("int a=5; int b=10; print(a > b);")
run_test("int a=5; int b=10; print(a == b);")
run_test("int a=5; int b=10; print(a != b);")

# print("\n=== Invalid Test Cases ===")
# run_test("int x=12; print(x")
# run_test("int x=12; int y=2; if (x < 4 { x=10; y=2} else { x=15; y=45}; print(y);")
# run_test("int x=12; int y=2; if x < 4) { x=10; y=2} else { x=15; y=45}; print(y);")
# run_test("int x=12; int y=2; if (x < 4) { x=10; y=2 else { x=15; y=45}; print(y);")
# run_test("int x=12; int y=2; if (x < 4) { x=10; y=2} elif (x < 8 ) { x=20; y=30 elif (x < 10) { x=40; y=60} else { x=15; y=45}; print(y);")  # Missing closing parenthesis in elif condition
# run_test("int x=12; int y=2; if (x < 4) { x=10; y=2} elif (x < 8 ) { x=20; y=30} elif (x < 10) { x=40; y=60} else { x=15; y=45; print(y);")  # Missing closing brace in else body

