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
class Break(AST):
    pass

@dataclass
class Continue(AST):
    pass
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
class ArrayAppend(AST):
    array: AST
    value: AST

@dataclass
class ArrayDelete(AST):
    array: AST
    index: AST

@dataclass
class Input(AST):
    type: str  

class SymbolTable:
    def __init__(self, parent=None):
        self.variables = {}  # Store variable_name: declared_type
        self.functions = {}   # Stores function_name: (return_type, param_types)
        self.parent = parent  # for nested scopes

    def declare_variable(self, name, declared_type):
        self.variables[name] = declared_type

    def lookup_variable(self, name):
        if name in self.variables:
            return self.variables[name]  # Returns type
        while self.parent:
            return self.parent.lookup_variable(name)
        raise NameError(f"Variable '{name}' is not declared")

    # def declare_function(self, name, return_type, param_types):
    #     """Declare a function with a return type and parameter types."""
    #     if name in self.functions:
    #         raise TypeError(f"Function '{name}' is already declared")

    #     self.functions[name] = (return_type, param_types)

    def lookup_function(self, name):
        """Retrieve function return type and parameter types."""
        if name in self.functions:
            return self.functions[name]  # Returns (return_type, param_types)
        if self.parent:
            return self.parent.lookup_function(name)
        raise NameError(f"Function '{name}' is not declared")

    def enter_scope(self):
        return SymbolTable(parent=self)

    def exit_scope(self):
        return self.parent

def infer_type(node):

    if isinstance(node, Number):
        return "int" if '.' not in node.val else "float" 
    if isinstance(node, String):
        return "string" 
    if isinstance(node, Boolean):
        return "bool"
    if isinstance(node, Variable):
        declared_type = symbol_table.lookup_variable(node.val)
        return declared_type
    
    if isinstance(node, Array):
        element_type = infer_type(node.elements[0])  # Assume homogeneous array
        return element_type + "[]"
    
    if isinstance(node, BinOp):
        left_type = infer_type(node.left)
        right_type = infer_type(node.right)

        # Ensure both operands have the same type
        if left_type != right_type:
            raise TypeError(f"Type mismatch in binary operation '{node.op}': {left_type} and {right_type}")

        return left_type  

    if isinstance(node, FunctionCall):  
        return_type, param_types = symbol_table.lookup_function(node.name)

        return return_type  # Return function return type

    raise TypeError(f"Unknown type for expression: {node}")

symbol_table = SymbolTable()

inside_function=False

class ParseError(Exception):
    def __init__(self, message, token):
        line_info = f"Error in line {getattr(token, 'line', 'unknown')}" if token else "Error"
        super().__init__(f"{line_info}: {message}")
        self.token = token
        self.message = message

def parse(s: str) -> AST:
    t = peekable(lex(s))
    
    def next_token():
        token = next(t, None)
        if token:
            token.line = getattr(token, 'line', 'unknown')  # Ensure line attribute exists
        return token

    def parse_sequence():
        statements = []
        
        while True:
            try:
                token=t.peek(None)
                if token is None:
                    break
                match t.peek(None): 
                    case KeywordToken("def"): 
                        
                        statements.append(parse_function())
                        
                    case KeywordToken("yeet"):
                        
                        if not inside_function:
                            raise ParseError("Return statement outside Function body", t.peek())
                        next_token()
                        expr = parse_comparator()
                        
                        # If returning an array, ensure it’s valid
                        # if isinstance(expr, Array):
                        #     if not inside_function:
                        #         raise ParseError("Return statement outside Function body", t.peek())
                       
                        statements.append(Return(expr))
                        
                        # while t.peek(None) and t.peek(None) != ParenthesisToken("}"):
                        #     next_token()
                        
                        break

                    case KeywordToken("yap"):
                        statements.append(parse_print())
                    case ParenthesisToken("}"):  
                        break
                    case _:
                        stmt = parse_condition()
                        
                        statements.append(stmt)
                
                if isinstance(statements[-1], (Cond,Function,For,While)):
                    pass 
                else: 
                    if isinstance(t.peek(None), SymbolToken) and t.peek(None).val == ";":
                        next_token()   
                    else:
                        raise ParseError("Expected ';' after statement", t.peek())

            except ParseError as e:
                print(e)
                break
        return Sequence(statements) 
                        
    def parse_function_call():
        try:
            match t.peek(None):
                case VariableToken(name):
                    token = next_token()

                    if t.peek(None) != ParenthesisToken("("):  # Not a function call, treat as expression
                        t.prepend(VariableToken(name))
                        return parse_comparator()

                    next_token()  # Consume '('
                    args = []
                    try:
                        return_type, param_types = symbol_table.functions[name]
                    except KeyError:
                        raise NameError(f"Function '{name}' is not declared")

                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == ")"):
                        args.append(parse_comparator())

                        if t.peek(None) == SymbolToken(","):
                            next_token()
                        else:
                            break

                    if next_token() != ParenthesisToken(")"):
                        raise ParseError("Expected ')' after function arguments", t.peek())

                    # Handle array operations like `arr.append(x)` and `arr.delete(index)`
                    if name.endswith(".append") and len(args) == 1:
                        array_name = name.split(".")[0]
                        return ArrayAppend(Variable(array_name), args[0])

                    if name.endswith(".delete") and len(args) == 1:
                        array_name = name.split(".")[0]
                        return ArrayDelete(Variable(array_name), args[0])


                    # **Check argument count**
                    if len(args) != len(param_types):
                        raise TypeError(f"Function '{name}' expects {len(param_types)} arguments, but got {len(args)}")

                    # **Check argument types**
                    for (expected_type, arg) in zip(param_types, args):
                        arg_type = infer_type(arg)
                        if arg_type != expected_type:
                            raise TypeError(f"Function '{name}' expected argument of type '{expected_type}' but got '{arg_type}'")
                       
                    result = FunctionCall(name, args)
                    result_type = infer_type(result)
                    if return_type != 'void' and result_type!=return_type:
                        raise TypeError(f"Function '{name}' expected return type '{return_type}' but got '{result_type}'")

                    return result_type

                case _:
                    return parse_comparator()
        except ParseError as e:
            print(e)
            return None


    def parse_function():
        try:
            match t.peek(None):
                case KeywordToken("def"):  # Function return type
                    next_token()

                    match t.peek(None):
                        case VariableToken(name):
                            next_token()
                            if next_token() != ParenthesisToken("("):
                                raise ParseError("Expected '(' after function name", t.peek())

                            params = []

                            while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == ")"):
                                param_type_token = next_token()
                                if not isinstance(param_type_token, TypeToken):
                                    raise TypeError("Expected type for function parameter", str(param_type_token))

                                param_type = param_type_token.val

                                # Check if it's an array parameter (e.g., int[] arr)
                                if t.peek(None) == ParenthesisToken("["):
                                    next_token()
                                    if next_token() != ParenthesisToken("]"):
                                        raise ParseError("Expected ']' for array parameter", t.peek())
                                    param_type += "[]"

                                param_name_token = next_token()
                                if not isinstance(param_name_token, VariableToken):
                                    raise ParseError(f"Expected a variable name, got {param_name_token}", t.peek())

                                param_name = param_name_token.val
                                params.append((param_type, param_name))

                                symbol_table.declare_variable(param_name, param_type)

                                if t.peek(None) == SymbolToken(","):
                                    next_token()
                                else:
                                    break
                            if next_token() != ParenthesisToken(")"):
                                raise ParseError("Expected ')' after function parameters", t.peek())

                            if t.peek(None) == SymbolToken("->"):
                                next_token()
                                if not isinstance(t.peek(None), TypeToken):
                                    raise TypeError("return type", str(t.peek(None)))
                                return_type = next_token().val
                                # Check if return type is an array (e.g., int[])
                                if t.peek(None) == ParenthesisToken("["):
                                    next_token()
                                    if next_token() != ParenthesisToken("]"):
                                        raise ParseError("Expected ']' for array return type", t.peek())
                                    return_type += "[]"  # Mark it as an array type
                            else:
                                return_type = 'void'

                            if next_token() != ParenthesisToken("{"):
                                raise ParseError("Expected { before function body", t.peek())

                            global inside_function
                            inside_function = True

                            # **Store function in the global symbol table before parsing the body to allow recursion**
                            symbol_table.functions[name] = (return_type, [ptype for ptype, _ in params])

                            function = Function(name, params, return_type, None)

                            function.body = parse_sequence()

                            if next_token() != ParenthesisToken("}"):
                                raise ParseError("Expected } after function body", t.peek())

                            inside_function = False

                            
                            return function

                        case _:
                            raise NameError("Expected function name")
        except ParseError as e:
            print(e)
            return None


        
    
    def parse_print():
        next_token()  # Consume 'print'
        
        if t.peek(None) != ParenthesisToken("("):
            raise ParseError("Expected '(' after print keyword", t.peek())
        next_token()  # Consume '('
        
        values = []
        while t.peek(None) and not isinstance(t.peek(None), ParenthesisToken):
            values.append(parse_comparator())  # Always use parse_comparator to handle full expressions
            
            if t.peek(None) == SymbolToken(","):
                next_token()  # Consume ','
            else:
                break

        if next_token() != ParenthesisToken(")"):
            raise ParseError("Expected ')' after print arguments", t.peek())

        return Print(values)

    def parse_condition():
        try:
            match t.peek(None):
                case KeywordToken('if'):
                    next_token() 

                    if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '(':
                        raise ParseError("Expected '(' after 'if' keyword", t.peek())

                    next_token() 
                    condition = parse_comparator()

                    closing_paren = next_token(None)  
                    if not isinstance(closing_paren, ParenthesisToken) or closing_paren.val != ')':
                        raise ParseError("Expected ')' after if condition", t.peek())

                    if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '{':
                        raise ParseError("Expected '{' after if condition", t.peek())
                    
                    next_token() 
                    if_branch = parse_sequence()
                    
                    
                    if t.peek(None) != ParenthesisToken('}'):
                        raise ParseError("Expected '}' after if body", t.peek())
                    next_token() 
                    
                    elif_branches = []
                    while isinstance(t.peek(None), KeywordToken) and t.peek(None).val == 'elif':
                        next_token()  

                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '(':
                            raise ParseError("Expected '(' after elif keyword", t.peek())

                        next_token() 
                        elif_condition = parse_comparator()

                        closing_paren = next_token(None)  
                        if not isinstance(closing_paren, ParenthesisToken) or closing_paren.val != ')':
                            raise ParseError("Expected ')' after elif condition", t.peek())
                        
                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '{':
                            raise ParseError("Expected '{' after elif condition", t.peek())

                        next_token()  
                        elif_body = parse_sequence()  
                        
                        if t.peek(None) != ParenthesisToken('}'):
                            raise ParseError("Expected '}' after elif body", t.peek())
                        next_token() 

                        elif_branches.append((elif_condition, elif_body))
                    
                    else_branch = None
                    if isinstance(t.peek(None), KeywordToken) and t.peek(None).val == 'else':
                        next_token()  

                        if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '{':
                            raise ParseError("Expected '{' after else keyword", t.peek())

                        next_token()  
                        else_branch = parse_sequence()  

                        
                        if t.peek(None) != ParenthesisToken('}'):
                            raise ParseError("Expected '}' after else body", t.peek())
                        next_token()  

                    return Cond((condition, if_branch), elif_branches, else_branch)

                case KeywordToken('for'):
                    next_token()
                    match t.peek(None):
                        case ParenthesisToken('('):
                            next_token()
                            init = parse_assignment()  # Parse initialization (e.g., int i = 0)

                            match next_token(None):
                                case SymbolToken(';'):
                                    pass
                                case _:
                                    raise ParseError("Expected ';' after for-loop initialization", t.peek())

                            condition = parse_comparator()  # Parse condition (e.g., i < 10)

                            match next_token(None):
                                case SymbolToken(';'):
                                    pass
                                case _:
                                    raise ParseError("Expected ';' after for-loop condition", t.peek())

                            increment = parse_assignment()  # Parse increment (e.g., i = i + 1)

                            match next_token(None):
                                case ParenthesisToken(')'):
                                    pass
                                case _:
                                    raise ParseError("Expected ')' after for-loop increment", t.peek())

                        case _:
                            raise ParseError("Expected '(' after 'for' keyword", t.peek())

                    match t.peek(None):
                        case ParenthesisToken('{'):
                            next_token()
                            body = parse_sequence()  # Parse the body of the for loop
                            
                            if t.peek(None) != ParenthesisToken('}'):
                                raise ParseError("Expected '}' after for-loop body", t.peek())
                            next_token()  # Consume '}'
                            return For(init, condition, increment, body)

                        case _:
                            raise ParseError("Expected '{' after for-loop definition", t.peek())

                case KeywordToken('while'):
                    next_token()
                    match t.peek(None):
                        case ParenthesisToken('('):
                            next_token()
                            condition = parse_comparator()
                            match next_token(None):
                                case ParenthesisToken(')'):
                                    pass
                                case _:
                                    raise ParseError("Expected ')' after while condition", t.peek())
                        case _:
                            raise ParseError("Expected '(' after 'while' keyword", t.peek())
                    
                    match t.peek(None):
                        case ParenthesisToken('{'):
                            next_token()
                            body = parse_sequence()  # Parse the body of the while loop
                            
                            if t.peek(None) != ParenthesisToken('}'):
                                raise ParseError("Expected '}' after while-loop body", t.peek())
                            next_token()  # Consume '}'
                            return While(condition, body)
                        case _:
                            raise ParseError("Expected '{' after while condition", t.peek())
                case KeywordToken('break'):
                    next_token()  # Consume 'break'
                    if t.peek(None) != SymbolToken(';'):
                        raise ParseError("Expected ';' after 'break'", t.peek())
                    return Break()

                case KeywordToken('continue'):
                    next_token()  # Consume 'continue'
                    if t.peek(None) != SymbolToken(';'):
                        raise ParseError("Expected ';' after 'continue'", t.peek())
                    return Continue()
                case _:
                    return parse_assignment()
        except ParseError as e:
            print(e)
            return None

    def parse_assignment():
        try:
            match t.peek(None):
                case VariableToken(var_name):
                    next_token()
                    match t.peek(None):
                        case OperatorToken('='):  # assignment
                            next_token()
                            value = parse_comparator()

                            expected_type = symbol_table.lookup_variable(var_name)
                            actual_type = infer_type(value)

                            if expected_type != actual_type:
                                raise TypeError(f"Cannot assign {actual_type} to {expected_type}")

                            return Assignment(var_name, value)

                        case ParenthesisToken('('):  # Function call
                            t.prepend(VariableToken(var_name))
                            return parse_function_call()

                        case ParenthesisToken('['):  # Array access or assignment
                            next_token()
                            index = parse_comparator()

                            if next_token() != ParenthesisToken(']'):
                                raise ParseError("Expected ']' after array index", t.peek())

                            # **💡 Type Checking: Ensure index is an integer**
                            if infer_type(index) != "int":
                                raise TypeError("Array index must be an integer")

                            if t.peek(None) == OperatorToken('='):
                                next_token()
                                value = parse_comparator()
                                return ArrayAssignment(Variable(var_name), index, value)
                            return ArrayAccess(Variable(var_name), index)

                        case _:
                            t.prepend(VariableToken(var_name))
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
                        raise NameError("Invalid type", var_type)
                    else:
                        next_token()
                        match t.peek(None):
                            case VariableToken(var_name):
                                if var_name in keywords:
                                    raise InvalidVariableNameError(var_name)
                                else:
                                    next_token()
                                    match t.peek(None):
                                        case OperatorToken('='):
                                            next_token()
                                            value = parse_function_call()

                                            # Check if value is an array access
                                            if isinstance(value, Variable) and t.peek(None) == ParenthesisToken('['):
                                                next_token()
                                                index = parse_comparator()
                                                if next_token() != ParenthesisToken(']'):
                                                    raise ParseError("Expected ']' after array index", t.peek())
                                                value = ArrayAccess(value, index)  # Convert to ArrayAccess node

                                            # **💡 Type Checking: Ensure value type matches declared type**
                                            value_type = infer_type(value)
                                            if value_type != var_type:
                                                raise TypeError(f"Cannot assign {value_type} to {var_type}")

                                            symbol_table.declare_variable(var_name, var_type)
                                            return Declaration(var_type, var_name, value)

                                        case ParenthesisToken('['):  # Array declaration
                                            next_token()
                                            elements = []
                                            while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == "]"):
                                                elements.append(parse_comparator())
                                                if t.peek(None) == SymbolToken(","):
                                                    next_token()
                                                else:
                                                    break
                                            if next_token() != ParenthesisToken("]"):
                                                raise ParseError("Expected ']' after array elements", t.peek())

                                            # **💡 Type Checking: Ensure all array elements match var_type**
                                            element_types = {infer_type(e) for e in elements}
                                            if len(element_types) > 1 or var_type not in element_types:
                                                raise TypeError(f"Array elements must be of type {var_type}")

                                            symbol_table.declare_variable(var_name, var_type + "[]")
                                            return Declaration(var_type + "[]", var_name, Array(elements))

                                        case _:
                                            raise ParseError("Expected '=' or '[' after variable name", t.peek())
                            case _:
                                raise ParseError("Expected variable name after type", t.peek())
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
                        if op in {"<", ">", "<=", ">=", "==", "!="}:  # added <=, >= and !=
                            next_token()
                            ast = BinOp(op, ast, parse_add())
                        elif op in {"and", "or"}:
                            next_token()
                            ast = BinOp(op, ast, parse_add())
                        elif op in {"not"}:
                            next_token()
                            ast = BinOp(op, ast, parse_add())
                        elif op == "&":  # Bitwise AND
                            next_token()
                            ast = BinOp("&", ast, parse_add())
                        elif op == "|":  # Bitwise OR
                            next_token()
                            ast = BinOp("|", ast, parse_add())
                        elif op == "~~":  # Bitwise NOT (unary)
                            next_token()
                            ast = BinOp("~~", None, parse_add())  # Unary operator
                        else:
                            raise InvalidOperationError(str(op), "comparison")
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
                        next_token()
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
                        next_token()
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
                        next_token()
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
                        next_token()
                        ast = BinOp('/', ast, parse_exponent())
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
                        next_token()
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
                    next_token()
                    match t.peek(None):
                        case ParenthesisToken('('):
                            next_token()
                            left = parse_atom()
                            match t.peek(None):
                                case OperatorToken(','):
                                    next_token()
                                    right = parse_atom()
                                    match t.peek(None):
                                        case ParenthesisToken(')'):
                                            next_token()
                                            return Concat(left, right)
                                        case _:
                                            raise ParseError("Expected ')' after concat arguments", t.peek())
                                case _:
                                    raise ParseError("Expected ',' after first concat argument", t.peek())
                        case _:
                            raise ParseError("Expected '(' after 'concat'", t.peek())
                case OperatorToken('~~'):
                    next_token()
                    return BinOp("~~", None, parse_atom())
                case OperatorToken('~'):  # Check for the tilde operator
                    next_token()
                    return BinOp('*', Number('-1'), parse_atom())
                case VariableToken(v):
                    next_token()
                    # Check if this variable is an array accessing term
                    if t.peek(None) == ParenthesisToken('['):
                        next_token()
                        index = parse_comparator()
                        if next_token() != ParenthesisToken(']'):
                            raise ParseError("Expected ']' after array index", t.peek())
                        return ArrayAccess(Variable(v), index)
                      # If no `[`, treat as normal variable
                    
                    if t.peek(None) == ParenthesisToken("("):
                        t.prepend(VariableToken(v))
                        return parse_function_call()
                    
                    return Variable(v)
                case NumberToken(v):
                    next_token()
                    return Number(v)
                case BooleanToken(v):
                    next_token()
                    return Boolean(v)
                case ParenthesisToken('('):
                    next_token()
                    expr = parse_comparator()
                    match next_token(None):
                        case ParenthesisToken(')'):
                            return Parenthesis(expr)
                        case _:
                            raise ParseError("Expected ')' after expression", t.peek())
                case StringToken(v):
                    next_token()
                    return String(v)
                case ParenthesisToken('['):
                    next_token()
                    elements = []
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == "]"):
                        elements.append(parse_comparator())
                        if t.peek(None) == SymbolToken(","):
                            next_token()
                        else:
                            break
                    if next_token() != ParenthesisToken("]"):
                        raise ParseError("Expected ']' after array elements", t.peek())
                    return Array(elements)
                
                case _:
                    raise ParseError(f"Unexpected token: {t.peek(None)}", t.peek())
        except ParseError as e:
            print(e)
            next_token()
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



