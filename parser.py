from dataclasses import dataclass
from more_itertools import peekable
from typing import Optional, List
from keywords import keywords, datatypes
from lexer import *
from errors import *

class AST:
    pass

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

@dataclass
class Cond(AST):
    If: tuple[AST, AST]  # ('condition', 'body') for the 'if' statement
    Elif: Optional[List[tuple[AST, AST]]] # Optional list of ('condition', 'body') for each 'elif'
    Else: Optional[AST] = None 
    
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

@dataclass
class Number(AST):
    val: str

@dataclass
class Parenthesis(AST):
    expr: AST

@dataclass
class SemicolonToken(AST):
    s: str

@dataclass
class Boolean(AST):
    val: str

@dataclass
class String(AST):
    val: str

@dataclass
class Variable(AST):
    val: str

@dataclass
class Declaration(AST):
    type: str
    name: str
    value: AST

@dataclass
class Assignment(AST):
    name: str
    value: AST

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

@dataclass
class Print(AST):
    values: list[AST]  

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


MAX_RECURSION_DEPTH = 1000  # Prevent infinite recursion
function_call_stack = []



def parse(s: str) -> AST:
    t = peekable(lex(s))

    def parse_sequence(inside_function=False):
        statements = []
        
        while True:
            try:
                token=t.peek(None)
                if token is None:
                    break
                match t.peek(None): 
                    case KeywordToken("def"):  
                        statements.append(parse_function())
                    case KeywordToken("return"):
                        if not inside_function:
                            raise ParseError("Return statement outside Function body", t.peek())
                        next(t)
                        expr = parse_function_call()
                        statements.append(Return(expr))
                    case KeywordToken("print"):
                        statements.append(parse_print())
                    case ParenthesisToken('}'):
                        # next(t)  
                        break 
                    case _:
                        stmt = parse_condition()
                        statements.append(stmt)

                #  Allow both ; and \n as optional separators
                while isinstance(t.peek(None), (SymbolToken, NewlineToken)):
                    token = t.peek(None)
                    if isinstance(token, SymbolToken) and token.val == ";":
                        next(t)  
                    elif isinstance(token, NewlineToken):
                        next(t) 
                    else:
                        break 

            except ParseError as e:
                print(e)
                break
        return Sequence(statements) if len(statements) > 1 else statements[0]

    
    def parse_print():
        next(t)  # Consume 'print'
        if t.peek(None) != ParenthesisToken("("):
            raise ParseError("Expected '(' after print keyword", t.peek())
        next(t)  # Consume '('
        
        values = []
        while t.peek(None) and not isinstance(t.peek(None), ParenthesisToken):
            if isinstance(t.peek(None), VariableToken):
                var_name = next(t).val
                if t.peek(None) == ParenthesisToken('['):
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

            
        return Print(values)
                        
    def parse_function_call():
        try:
            match t.peek(None):
                case VariableToken(name):
                    next(t) 

                    if next(t) != ParenthesisToken("("):
                        raise ParseError("Expected '(' after function name", t.peek())

                    args = []
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == ")"):
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
                            
                                # **Store function before parsing the body to allow recursion**
                            function = Function(name, params, return_type, None)

                            function.body = parse_sequence(inside_function=True)

                            if next(t) != ParenthesisToken("}"):
                                raise ParseError("Expected } after function body", t.peek())
                            
                            return function
                        case _:
                            raise ParseError("Expected function name after 'def'", t.peek())
        except ParseError as e:
            print(e)
            return None

    def parse_condition():
        try:
            match t.peek(None):
                case KeywordToken('if'):
                    next(t) 

                    if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '(':
                        raise ParseError("Expected '(' after 'if' keyword", t.peek())

                    next(t) 
                    condition = parse_comparator()

                    closing_paren = next(t, None)  
                    if not isinstance(closing_paren, ParenthesisToken) or closing_paren.val != ')':
                        raise ParseError("Expected ')' after if condition", t.peek())

                    if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '{':
                        raise ParseError("Expected '{' after if condition", t.peek())

                    next(t) 
                    if_branch = parse_sequence()
                    
                    if t.peek(None) != ParenthesisToken('}'):
                        raise ParseError("Expected '}' after if body", t.peek())
                    next(t) 
                    while isinstance(t.peek(None), NewlineToken):
                        next(t)
                    elif_branches = []
                    while isinstance(t.peek(None), KeywordToken) and t.peek(None).val == 'elif':
                        next(t)  

                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '(':
                            raise ParseError("Expected '(' after elif keyword", t.peek())

                        next(t) 
                        elif_condition = parse_comparator()

                        closing_paren = next(t, None)  
                        if not isinstance(closing_paren, ParenthesisToken) or closing_paren.val != ')':
                            raise ParseError("Expected ')' after elif condition", t.peek())
                        
                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '{':
                            raise ParseError("Expected '{' after elif condition", t.peek())

                        next(t)  
                        elif_body = parse_sequence()  
                        if t.peek(None) != ParenthesisToken('}'):
                            raise ParseError("Expected '}' after elif body", t.peek())
                        next(t) 

                        elif_branches.append((elif_condition, elif_body))
                    
                    else_branch = None
                    print(t.peek(None))
                    if isinstance(t.peek(None), KeywordToken) and t.peek(None).val == 'else':
                        next(t)  
                        print(t.peek(None))

                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '{':
                            raise ParseError("Expected '{' after else keyword", t.peek())

                        next(t)  
                        else_branch = parse_sequence()  
                        if t.peek(None) != ParenthesisToken('}'):
                            raise ParseError("Expected '}' after else body", t.peek())
                        next(t)  

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

                    while isinstance(t.peek(None), NewlineToken):
                        next(t)
                    match t.peek(None):
                        case ParenthesisToken('{'):
                            next(t)
                            body = parse_sequence()  # Parse the body of the for loop
                            while isinstance(t.peek(None), NewlineToken):
                                next(t)
                            if t.peek(None) != ParenthesisToken('}'):
                                print(t.peek())
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
                    while isinstance(t.peek(None), NewlineToken):
                        next(t)
                    match t.peek(None):
                        case ParenthesisToken('{'):
                            next(t)
                            body = parse_sequence()  # Parse the body of the while loop
                            while isinstance(t.peek(None), NewlineToken):
                                next(t)
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
                                            if isinstance(t.peek(None), VariableToken) and t.peek(None).val == "input":
                                                next(t)  # consume 'input'
                                                if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '(':
                                                    raise ParseError("Expected '(' after input", t.peek())
                                                next(t)
                                                if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != ')':
                                                    raise ParseError("Expected ')' after input", t.peek())
                                                next(t) 
                                                return Declaration(var_type, var_name, Input(var_type))
                                            value = parse_comparator()
                                            return Declaration(var_type, var_name, value)
                                        case ParenthesisToken('['):  # Array declaration
                                            next(t)
                                            elements = []
                                            while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == "]"):
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
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == "]"):
                        elements.append(parse_comparator())
                        if t.peek(None) == SymbolToken(","):
                            next(t)
                        else:
                            break
                    if next(t) != ParenthesisToken("]"):
                        raise ParseError("Expected ']' after array elements", t.peek())
                    return Array(elements)
                case NewlineToken():
                    next(t) 
                case _:
                    raise ParseError(f"Unexpected token: {t.peek(None)}", t.peek())
        except ParseError as e:
            print(e)
            next(t)
            return None

    return parse_sequence()

# def run_test(code):
#     try:
#         print(f"\nExecuting: {code}")
#         ast = parse(code)
#         if ast is None:
#             print("Failed to parse the code")
#             return
#         e(ast)  # Just execute, don't print result
#     except Exception as ex:
#         print(f"Error: {ex}\n")



