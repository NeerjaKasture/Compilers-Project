from dataclasses import dataclass
from more_itertools import peekable
from typing import Optional, List
from keywords import keywords, datatypes
from lexer import *
from errors import *

# helper‑method names recognised after an array / array element
METHODS = {"append", "delete", "len"}

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

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return False
        return self.statements == other.statements

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
class ArrayLength(AST):
    array: AST


@dataclass
class Input(AST):
    pass

@dataclass
class StackDeclaration(AST):
    element_type: str
    name: str

@dataclass
class StackPush(AST):
    stack_name: str
    value: AST

@dataclass
class StackPop(AST):
    stack_name: str

@dataclass
class StackTop(AST):
    stack_name: str

@dataclass
class QueueDeclaration(AST):
    element_type: str 
    name: str

@dataclass
class QueuePush(AST):
    queue_name: str
    value: AST

@dataclass
class QueuePop(AST):
    queue_name: str

@dataclass
class QueueFirst(AST):
    queue_name: str

@dataclass
class HashMap(AST):
    name: str
    index_type: str
    value_type: str

@dataclass
class StructDefinition(AST):
    name: str
    fields: list[tuple[str, str]]  # List of (type, name)

inside_function=False

def parse(s: str) -> AST:
    t = peekable(lex(s))

    # debug prints while adding line numbers in errors
    # print(list(t))
    # print(t.peek(None))
    # print(isinstance(t.peek(None), KeywordToken))
    # print(isinstance(t.peek(None), KeywordToken) and t.peek(None).val == "yap")
    # print(t.peek(None) == KeywordToken("yap"))

    def parse_sequence():
        statements = []
        
        while True:
            try:
                token=t.peek(None)
                last_token = token
                if token is None:
                    break
                match t.peek(None): 
                    case KeywordToken("def"): 
                        
                        statements.append(parse_function())
                        
                    case KeywordToken("yeet"):
                        
                        # if not inside_function:
                        #     raise ParseError("Return statement outside Function body", t.peek())
                        next(t)
                        expr = parse_comparator()
                        
                        # If returning an array, ensure it’s valid
                        # if isinstance(expr, Array):
                        #     if not inside_function:
                        #         raise ParseError("Return statement outside Function body", t.peek())
                       
                        statements.append(Return(expr))
                        
                        # while t.peek(None) and t.peek(None) != ParenthesisToken("}"):
                        #     next(t)
                        
                        break

                    case KeywordToken("yap"):
                        statements.append(parse_print())
                    case ParenthesisToken("}"):  
                        break
                    case KeywordToken("struct"):
                        statements.append(parse_struct())
                    case _:
                        
                        stmt = parse_condition()
                        statements.append(stmt)
                
                if isinstance(statements[-1], (Cond,Function,For,While)):
                    pass 
                else: 
                    if isinstance(t.peek(None), SymbolToken) and t.peek(None).val == ";":
                        next(t)   
                    else:
                        raise ParseError("Expected ';' after statement", last_token)

            except ParseError as e:
                raise e
        return Sequence(statements) 
                        
    def parse_function_call():
        try:
            
            match t.peek(None):
                
                case VariableToken(name):
                    next(t) 

                    if t.peek(None) != ParenthesisToken("("):
                        t.prepend(VariableToken(name))
                        return parse_comparator()
                    
                    next(t)
                    last_token = t.peek(None)
                    args = []
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == ")"):
                        args.append(parse_comparator())
                        if t.peek(None):
                            last_token = t.peek(None)

                        if t.peek(None) == SymbolToken(","):
                            next(t)
                        else:
                            break
                    
                    # if next(t) != ParenthesisToken(")"):
                    #     raise ParseError("Expected ')' after function arguments", t.peek(None))

                    try:
                        closing = next(t)
                        if closing != ParenthesisToken(")"):
                            raise ParseError("Expected ')' after function arguments", last_token)
                    except StopIteration:
                        # Fall back to the last meaningful token for location info
                        raise ParseError("Unexpected end of input, expected ')'", last_token)

                    last_token = t.peek(None)
                    # Checking queue operations
                    if name.endswith(".stackPush"):
                        if len(args) != 1:
                            raise ParseError(f"Stack push expects exactly 1 argument, got {len(args)}", last_token)
                        stack_name = name.split(".")[0]
                        return StackPush(stack_name, args[0])

                    if name.endswith(".stackPop") and len(args) == 0:
                        stack_name = name.split(".")[0]
                        return StackPop(stack_name)

                    if name.endswith(".top") and len(args) == 0:
                        stack_name = name.split(".")[0]
                        return StackTop(stack_name)
                    
                    if name.endswith(".queuePush"):
                        if len(args) != 1:
                            raise ParseError(f"Queue push expects exactly 1 argument, got {len(args)}", last_token)
                        queue_name = name.split(".")[0]
                        return QueuePush(queue_name, args[0])

                    if name.endswith(".queuePop") and len(args) == 0:
                        queue_name = name.split(".")[0]
                        return QueuePop(queue_name)

                    if name.endswith(".first") and len(args) == 0:
                        queue_name = name.split(".")[0]
                        return QueueFirst(queue_name)
                    
                    # Check for stack operations
                    # if name.endswith(".push"):
                    #     if len(args) != 1:
                    #         raise ParseError(f"Stack push expects exactly 1 argument, got {len(args)}")
                    #     stack_name = name.split(".")[0]
                    #     return StackPush(stack_name, args[0])
                    # if name.endswith(".pop") and len(args) == 0:
                    #     stack_name = name.split(".")[0]
                    #     return StackPop(stack_name)
                    # if name.endswith(".top") and len(args) == 0:
                    #     stack_name = name.split(".")[0]
                    #     return StackTop(stack_name)
                    
                    # Check for array operations
                    if name.endswith(".append") and len(args) == 1:
                        array_name = name.split(".")[0]
                        return ArrayAppend(Variable(array_name), args[0])

                    if name.endswith(".delete") and len(args) == 1:
                        array_name = name.split(".")[0]
                        return ArrayDelete(Variable(array_name), args[0])
                    
                    if name.endswith(".len"):
                        array_name = name.split(".")[0]
                        if len(args) != 0:
                            raise ParseError("len function takes no arguments", t.peek())
                        return ArrayLength(Variable(array_name))
                    
                    return FunctionCall(name, args)
                case _:
                    return parse_comparator()
        except ParseError as e:
            raise e

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
                            
                            while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == ")"):
                                param_type_token = next(t)

                                if isinstance(param_type_token, TypeToken):
                                    param_type = param_type_token.val
                                elif isinstance(param_type_token, KeywordToken) and param_type_token.val == "fn":
                                    param_type = "fn"
                                else:
                                    raise TypeError("Expected type for function parameter", str(param_type_token))

                                # Check if it's an array parameter (e.g., int[] arr)
                                if t.peek(None) == ParenthesisToken("["):
                                    next(t)
                                    if next(t) != ParenthesisToken("]"):
                                        raise ParseError("Expected ']' for array parameter", t.peek())
                                    param_type += "[]"

                                param_name_token = next(t)

                                if not isinstance(param_name_token, VariableToken):
                                    raise ParseError(f"Expected a variable name, got {param_name_token}", t.peek())

                                param_name = param_name_token.val

                                params.append((param_type, param_name))

                                if t.peek(None) == SymbolToken(","):
                                    next(t)
                                else:
                                    break
                            if next(t) != ParenthesisToken(")"):
                                raise ParseError("Expected ')' after function parameters", t.peek())

                            if t.peek(None) == SymbolToken("->"):
                                next(t)
                                if isinstance(t.peek(None), TypeToken):
                                    return_type = next(t).val
                                elif isinstance(t.peek(None), KeywordToken) and t.peek(None).val == "fn":
                                    return_type = "fn"
                                    next(t)
                                else:
                                    raise TypeError("Expected return type after '->'", t.peek())
                                # Check if return type is an array (e.g., int[])
                                while t.peek(None) == ParenthesisToken("["):
                                    next(t)
                                    if next(t) != ParenthesisToken("]"):
                                        raise ParseError("Expected ']' for array return type", t.peek())
                                    return_type += "[]"  # Mark it as an array type
                            else:
                                return_type = 'void'

                            
                            if next(t) != ParenthesisToken("{"):
                                raise ParseError("Expected { before function body", t.peek())
                            

                            global inside_function
                            inside_function=True

                                # **Store function before parsing the body to allow recursion**
                            function = Function(name, params, return_type, None)
                            

                            function.body = parse_sequence()
                            
                            
                            if next(t) != ParenthesisToken("}"):
                               raise ParseError("Expected } after function body", t.peek())
                            
                            inside_function=False
                            return function
                        
                        case _:
                            raise NameError("function name")
        except ParseError as e:
            raise e
        
    
    def parse_print():
        next(t)  # Consume 'print'
        
        if t.peek(None) != ParenthesisToken("("):
            raise ParseError("Expected '(' after print keyword", t.peek())
        next(t)  # Consume '('
        
        values = []
        while t.peek(None) and  t.peek(None).val != ")":
            
            values.append(parse_comparator())  # Always use parse_comparator to handle full expressions
            if t.peek(None) == SymbolToken(","):
                next(t)  # Consume ','
            else:
                break
        
        # print(t.peek(None)) # debug
        if next(t) != ParenthesisToken(")"):
            raise ParseError("Expected ')' after print arguments", t.peek())

        return Print(values)

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
                    if isinstance(t.peek(None), KeywordToken) and t.peek(None).val == 'else':
                        next(t)  

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
                case KeywordToken('break'):
                    next(t)  # Consume 'break'
                    if t.peek(None) != SymbolToken(';'):
                        raise ParseError("Expected ';' after 'break'", t.peek())
                    return Break()

                case KeywordToken('continue'):
                    next(t)  # Consume 'continue'
                    if t.peek(None) != SymbolToken(';'):
                        raise ParseError("Expected ';' after 'continue'", t.peek())
                    return Continue()
                case _:
                    return parse_assignment()
        except ParseError as e:
            print(e)
            return None
        
    def parse_struct():
        try:
            match t.peek(None):
                case KeywordToken("struct"):
                    next(t)  # Consume 'struct'
                    if not isinstance(t.peek(None), VariableToken):
                        raise ParseError("Expected struct name after 'struct'", t.peek())
                    struct_name = t.peek(None).val
                    next(t)  # Consume struct name
                    if t.peek(None) != ParenthesisToken("{"):
                        raise ParseError("Expected '{' after struct name", t.peek())
                    next(t)  # Consume '{'
                    fields = []

                    while True:
                        if t.peek(None) == ParenthesisToken("}"):
                            break
                        if isinstance(t.peek(None),TypeToken):
                            field_type = next(t).val
                        elif isinstance(t.peek(None), KeywordToken) and t.peek(None).val == "fn":
                            field_type = "fn"
                            next(t)
                        else:
                            raise ParseError("Expected type for struct field", t.peek())
                        if t.peek(None) == ParenthesisToken("["):
                            next(t)
                            if next(t) != ParenthesisToken("]"):
                                raise ParseError("Expected ']' for array field", t.peek())
                            field_type += "[]"

                        if not isinstance(t.peek(None), VariableToken):
                            raise ParseError("Expected variable name for struct field", t.peek())
                        field_name = next(t).val
                        fields.append((field_type, field_name))
                        if t.peek(None) == SymbolToken(";"):
                            next(t)
                        else:
                            raise ParseError("Expected ';' after struct field", t.peek())
                    
                    if t.peek(None) != ParenthesisToken("}"):
                        raise ParseError("Expected '}' after struct fields", t.peek())
                    next(t)  # Consume '}'
                    return StructDefinition(struct_name, fields)
                case _:
                    pass
        except ParseError as e:
            print(e)
            return None  

    def parse_assignment():
        try:
            # not a variable ⇒ let declaration / general expression handle it
            if not isinstance(t.peek(None), VariableToken):
                return parse_declaration()

            # 1) consume the variable name
            var_tok  = next(t)                      # VariableToken
            var_name = var_tok.val
            node: AST = Variable(var_name)

            # 2) zero‑or‑more “[ index ]”  ⇒ build ArrayAccess chain
            has_index = False
            while t.peek(None) == ParenthesisToken('['):
                has_index = True
                next(t)                             # '['
                idx_ast = parse_comparator()
                if next(t) != ParenthesisToken(']'):
                    raise ParseError("Expected ']' after array index", t.peek())
                node = ArrayAccess(node, idx_ast)

            # 3) simple or element assignment?  (look for '=')
            if t.peek(None) == OperatorToken('='):
                next(t)                             # consume '='

                # -- special case -------------------------------------------------
                #    t = spill();
                # -----------------------------------------------------------------
                if (isinstance(t.peek(None), KeywordToken)
                        and t.peek(None).val == "spill"):
                    next(t)                         # 'spill'
                    if (next(t) != ParenthesisToken('(')
                            or next(t) != ParenthesisToken(')')):
                        raise ParseError("Expected empty spill()", t.peek())
                    rhs_ast = Input()
                else:
                    rhs_ast = parse_comparator()

                if has_index:                       # arr[i][j] = …
                    return ArrayAssignment(node, None, rhs_ast)
                else:                               # x = …
                    return Assignment(var_name, rhs_ast)

            # 4) not an assignment  → parse as expression (method chains allowed)
            while isinstance(t.peek(None), SymbolToken) and t.peek(None).val == '.':
                next(t)                             # '.'
                if not isinstance(t.peek(None), VariableToken):
                    raise ParseError("Expected method name after '.'", t.peek())
                method = next(t).val
                if method not in METHODS:           # {"append","delete","len"}
                    raise ParseError(f"Unknown method '{method}'", t.peek())
                if next(t) != ParenthesisToken('('):
                    raise ParseError("Expected '(' after method", t.peek())

                arg = None
                if method in {"append", "delete"}:
                    arg = parse_comparator()
                if next(t) != ParenthesisToken(')'):
                    raise ParseError("Expected ')' after method call", t.peek())

                node = (ArrayAppend(node, arg)  if method == "append" else
                        ArrayDelete(node, arg)  if method == "delete" else
                        ArrayLength(node))

            # optional plain function call (only if no “[ … ]” used)
            if not has_index and t.peek(None) == ParenthesisToken('('):
                t.prepend(VariableToken(var_name))
                return parse_function_call()

            return node                              # expression head

        except ParseError as e:
            raise e

    def parse_declaration():
        try:
            match t.peek(None):
                case KeywordToken("queue"):
                    next(t)  # Consume 'queue'
                    if t.peek(None) != OperatorToken('<'):
                        raise ParseError("Expected '<' after 'queue'", t.peek())
                    next(t)  # Consume '<'
                    if not isinstance(t.peek(None), TypeToken):
                        raise ParseError("Expected type after '<'", t.peek())
                    element_type = next(t).val

                    if t.peek(None) != OperatorToken('>'):
                        raise ParseError("Expected '>' after queue element type", t.peek())
                    next(t)

                    if not isinstance(t.peek(None), VariableToken):
                        raise ParseError("Expected queue name after '>'", t.peek())
                    queue_name = next(t).val
                    if queue_name in keywords:
                        raise InvalidVariableNameError(queue_name)
                    if t.peek(None) != SymbolToken(";"):
                        raise ParseError("Expected ';' after queue declaration", t.peek())
                    
                    return QueueDeclaration(element_type, queue_name)
                
                case KeywordToken("stack"):
                     next(t)  # Consume 'stack'
                     if t.peek(None) != OperatorToken('<'):
                         raise ParseError("Expected '<' after 'stack'", t.peek())
                     next(t)  # Consume '<'
                     if not isinstance(t.peek(None), TypeToken):
                         raise ParseError("Expected type after '<'", t.peek())
                     element_type = next(t).val
 
                     if t.peek(None) != OperatorToken('>'):
                         raise ParseError("Expected '>' after stack element type", t.peek())
                     next(t)
 
                     if not isinstance(t.peek(None), VariableToken):
                         raise ParseError("Expected stack name after '>'", t.peek())
                     stack_name = next(t).val
                     if stack_name in keywords:
                         raise InvalidVariableNameError(stack_name)
                     if t.peek(None) != SymbolToken(";"):
                         raise ParseError("Expected ';' after stack declaration", t.peek())
                     
                     return StackDeclaration(element_type, stack_name)
                
                case KeywordToken("hashmap"):
                    next(t)  # Consume 'hashmap'
                    if t.peek(None) != OperatorToken('<'):
                        raise ParseError("Expected '<' after 'hashmap'", t.peek())
                    next(t)  # Consume '<'
                    if not isinstance(t.peek(None), TypeToken):
                        raise ParseError("Expected key type after '<'", t.peek())
                    key_type = next(t).val
                    if t.peek(None) != SymbolToken(','):
                        raise ParseError("Expected ',' after key type", t.peek())
                    next(t)  # Consume ','
                    if not isinstance(t.peek(None), TypeToken):
                        raise ParseError("Expected value type after ','", t.peek())
                    value_type = next(t).val
                    if t.peek(None) != OperatorToken('>'):
                        raise ParseError("Expected closing '>' ", t.peek())
                    next(t)  # Consume '>'

                    if not isinstance(t.peek(None), VariableToken):
                        raise ParseError("Expected hashmap name after '>'", t.peek())
                    hashmap_name = next(t).val
                    if hashmap_name in keywords:
                        raise InvalidVariableNameError(hashmap_name)
                    if t.peek(None) != SymbolToken(";"):
                        raise ParseError("Expected ';' after hashmap declaration", t.peek())
                    
                    return HashMap(hashmap_name,key_type, value_type)
                    
                
                case TypeToken(var_type):
                    if var_type not in datatypes.keys():
                        raise TypeError("valid type", var_type)
                    else:
                        next(t)
                        match t.peek(None):
                            case VariableToken(var_name):
                                if var_name in keywords:
                                    raise InvalidVariableNameError(var_name)
                                else:
                                    next(t)
                                    match t.peek(None):
                                        case OperatorToken('='):
                                            next(t)
                                            if isinstance(t.peek(None), KeywordToken) and t.peek(None).val == "spill":
                                                next(t)  # consume 'input'
                                                if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != '(':
                                                    raise ParseError("Expected '(' after input", t.peek())
                                                next(t)
                                                if not isinstance(t.peek(None), ParenthesisToken) or t.peek(None).val != ')':
                                                    raise ParseError("Expected ')' after input", t.peek())
                                                next(t) 
                                                return Declaration(var_type, var_name, Input())
                                            value = parse_comparator()
                                            # **FIX: Ensure arr[0] is parsed as ArrayAccess**
                                            if isinstance(value, Variable) and t.peek(None) == ParenthesisToken('['):
                                                next(t)
                                                index = parse_comparator()
                                                if next(t) != ParenthesisToken(']'):
                                                    raise ParseError("Expected ']' after array index", t.peek())
                                                value = ArrayAccess(value, index)  # Convert to ArrayAccess node

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
                            case ParenthesisToken('['):  # Possibly multi-dimensional array type
                                array_depth = 0
                                while t.peek(None) == ParenthesisToken('['):
                                    next(t)
                                    if next(t) != ParenthesisToken(']'):
                                        raise ParseError("Expected ']' after '[' in array type", t.peek())
                                    array_depth += 1

                                match t.peek(None):
                                    case VariableToken(var_name):
                                        if var_name in keywords:
                                            raise InvalidVariableNameError(var_name)
                                        next(t)
                                        match t.peek(None):
                                            case OperatorToken('='):
                                                next(t)
                                                value = parse_comparator()
                                                return Declaration(var_type + "[]" * array_depth, var_name, value)
                                            case _:
                                                raise ParseError("Expected '=' after array variable name", t.peek())
                                    case _:
                                        raise ParseError("Expected variable name after array type", t.peek())

                case _:
                    return parse_comparator()
        except ParseError as e:
            raise e
        
    def parse_comparator():
        try:
            ast = parse_add()
            while True:
                match t.peek(None):
                    case OperatorToken(op):
                        if op in {"and", "or"}:  # added <=, >= and !=
                            next(t)
                            ast = BinOp(op, ast, parse_add())
                        elif op in {"not"}:
                            next(t)
                            ast = BinOp(op, None, parse_add())
                        elif op in {"<", ">", "<=", ">=", "==", "!="}:
                            next(t)
                            ast = BinOp(op, ast, parse_add())
                        elif op == "&":  # Bitwise AND
                            next(t)
                            ast = BinOp("&", ast, parse_add())
                        elif op == "|":  # Bitwise OR
                            next(t)
                            ast = BinOp("|", ast, parse_add())
                        elif op == "~~":  # Bitwise NOT (unary)
                            next(t)
                            ast = BinOp("~~", None, parse_add())  # Unary operator
                        else:
                            raise InvalidOperationError(str(op), "comparison")
                    case _:
                        return ast
        except ParseError as e:
            raise e

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
            raise e

    def parse_sub():
        try:
            ast = parse_mod()
            while True:
                match t.peek(None):
                    case OperatorToken('-'):
                        next(t)
                        ast = BinOp('-', ast, parse_mod())
                    case _:
                        return ast
        except ParseError as e:
            raise e

    def parse_mod():
        try:
            ast = parse_mul()
            while True:
                match t.peek(None):
                    case OperatorToken('%'):
                        next(t)
                        ast = BinOp('%', ast, parse_mul())
                    case _:
                        return ast
        except ParseError as e:
            raise e

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
            raise e

    def parse_div():
        try:
            ast = parse_modulo()  
            while True:
                match t.peek(None):
                    case OperatorToken('/'):
                        next(t)
                        ast = BinOp('/', ast, parse_modulo()) 
                    case OperatorToken('//'):
                        next(t)
                        ast = BinOp('//', ast, parse_modulo())
                    case _:
                        return ast
        except ParseError as e:
            raise e

    def parse_modulo():
        try:
            ast = parse_exponent()
            
            while True:
                match t.peek(None):
                    case OperatorToken('%'):
                        next(t)
                        ast = BinOp('%', ast, parse_exponent())  
                        
                    case _:
                        return ast
        except ParseError as e:
            raise e


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

                # ---------------------------------------------------------
                #  concat(left, right)
                # ---------------------------------------------------------
                case KeywordToken('concat'):
                    next(t)
                    if next(t) != ParenthesisToken('('):
                        raise ParseError("Expected '(' after 'concat'", t.peek())
                    left = parse_atom()
                    if next(t) != SymbolToken(','):
                        raise ParseError("Expected ',' after first concat arg", t.peek())
                    right = parse_atom()
                    if next(t) != ParenthesisToken(')'):
                        raise ParseError("Expected ')' after concat args", t.peek())
                    return Concat(left, right)

                # ---------------------------------------------------------
                #  unary operators:  not  ~~  ~
                # ---------------------------------------------------------
                case OperatorToken('not'):
                    next(t)
                    return BinOp('not', None, parse_atom())

                case OperatorToken('~~'):
                    next(t)
                    return BinOp('~~', None, parse_atom())

                case OperatorToken('~'):
                    next(t)
                    return BinOp('*', Number('-1'), parse_atom())

                # ---------------------------------------------------------
                #  VARIABLE  (with optional [idx]… and .append/.delete/.len)
                # ---------------------------------------------------------
                case VariableToken(v):
                    next(t)
                    node: AST = Variable(v)

                    # one or more “[ index ]” -> ArrayAccess chain
                    while t.peek(None) == ParenthesisToken('['):
                        next(t)                            # '['
                        idx = parse_comparator()
                        if next(t) != ParenthesisToken(']'):
                            raise ParseError("Expected ']' after array index", t.peek())
                        node = ArrayAccess(node, idx)

                    # zero or more “.method()” on the (sub)‑array
                    while isinstance(t.peek(None), SymbolToken) and t.peek(None).val == '.':
                        next(t)                            # '.'
                        if not isinstance(t.peek(None), VariableToken):
                            raise ParseError("Expected method name after '.'", t.peek())
                        method = next(t).val

                        if method not in METHODS:          # {"append","delete","len"}
                            raise ParseError(f"Unknown method '{method}'", t.peek())

                        if next(t) != ParenthesisToken('('):
                            raise ParseError("Expected '(' after method name", t.peek())

                        arg = None
                        if method in {"append", "delete"}: # need exactly one argument
                            arg = parse_comparator()

                        if next(t) != ParenthesisToken(')'):
                            raise ParseError("Expected ')' after method call", t.peek())

                        # build the new AST node and continue (method chaining allowed)
                        node = (ArrayAppend(node, arg)  if method == "append" else
                                ArrayDelete(node, arg)  if method == "delete" else
                                ArrayLength(node))      # len()

                    # a normal function call that immediately follows the variable
                    if t.peek(None) == ParenthesisToken('('):
                        t.prepend(VariableToken(v))
                        return parse_function_call()

                    return node

                # ---------------------------------------------------------
                #  literals, parenthesised expression, array literal
                # ---------------------------------------------------------
                case NumberToken(v):
                    next(t)
                    return Number(v)

                case BooleanToken(v):
                    next(t)
                    return Boolean(v)

                case ParenthesisToken('('):
                    next(t)
                    expr = parse_comparator()
                    if next(t) != ParenthesisToken(')'):
                        raise ParseError("Expected ')' after expression", t.peek())
                    return Parenthesis(expr)

                case StringToken(v):
                    next(t)
                    return String(v)

                case ParenthesisToken('['):                # array literal
                    next(t)
                    elements = []
                    while t.peek(None) and not (isinstance(t.peek(None), ParenthesisToken) and t.peek(None).val == "]"):
                        elements.append(parse_comparator())
                        if t.peek(None) == SymbolToken(','):
                            next(t)
                        else:
                            break
                    if next(t) != ParenthesisToken(']'):
                        raise ParseError("Expected ']' after array elements", t.peek())
                    return Array(elements)

                # ---------------------------------------------------------
                #  fallback
                # ---------------------------------------------------------
                case _:
                    raise ParseError(f"Unexpected token: {t.peek(None)}", t.peek())

        except ParseError as e:
            raise e

    return parse_sequence()



