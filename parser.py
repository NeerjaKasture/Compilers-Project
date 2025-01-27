from dataclasses import dataclass
from collections.abc import Iterator
from more_itertools import peekable
import sys

class AST:
    pass

@dataclass
class BinOp(AST):
    op: str
    left: AST
    right: AST  


@dataclass
class Cond(AST):
    If: AST
    Then: AST
    Else: AST

@dataclass
class Number(AST):
    val: str

@dataclass
class Parenthesis(AST):
    expr: AST

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

datatypes = {"int": int, "float": float, "bool": bool, "string": str}

def e(tree: AST, env={},types={}): # could also make the env dict global 
    match tree:
        case Variable(v):
            if v in env:
                return env[v]
            else:
                raise NameError(f"Undefined variable: {v}")
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
        case Cond(If, Then, Else):
            return e(Then) if e(If) else e(Else)
        case Declaration(var_type, var_name, value):
            val = e(value, env, types)

            if not isinstance(val, datatypes[var_type]):
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
        case String(v):
            return v
        case Concat(left, right):
            left_val = e(left, env, types)
            right_val = e(right, env, types)

            if not isinstance(left_val, str) or not isinstance(right_val, str):
                raise TypeError("Concat can only be used with String")

            return left_val + right_val 

       



class Token:
    pass


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

keywords = {"if", "then", "else", "true", "false","print","concat"}

def lex(s: str) -> Iterator[Token]:
    i = 0
    while i<len(s):
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
                else:
                    yield KeywordToken(word)
            else:
                yield VariableToken(word)

        elif s[i].isdigit():
            t = s[i]
            i += 1
            has_decimal=False
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
                case '+' | '*' | '-' | '/' | '^' | '(' | ')' | '<' | '>' | '=' | '!'| '~'|',':
                    if s[i] in '<>=!' and i + 1 < len(s) and s[i + 1] == '=':
                        yield OperatorToken(s[i:i + 2])
                        i += 2
                    else:
                        if s[i] in "()":
                            yield ParenthesisToken(s[i])
                        else:
                            yield OperatorToken(s[i])
                        i += 1
                case _:
                    raise SyntaxError(f"Unexpected character: {s[i]}")


def parse(s: str) -> AST:
    t = peekable(lex(s))

    def parse_condition():
        match t.peek(None):
            case KeywordToken('if'):  
                next(t)  
                condition = parse_comparator()  

                match t.peek(None):
                    case KeywordToken('then'):
                        next(t) 
                    case _:
                        raise SyntaxError("Expected 'then' after 'if' condition")

                then_branch = parse_condition()  

                match t.peek(None):
                    case KeywordToken('else'):
                        next(t) 
                    case _:
                        # should an if always have an else
                        # add else if later
                        raise SyntaxError("Expected 'else' after 'then' branch")

                else_branch = parse_condition() 
                return Cond(condition, then_branch, else_branch)

            case _:
                return parse_assignment() 
    
    def parse_assignment():
        match t.peek(None):
            case VariableToken(var_name):
                next(t)
                match t.peek(None):
                    case OperatorToken('='):
                        next(t)
                        value = parse_comparator()
                        return Assignment(var_name, value)
                    case _:
                        t.prepend(VariableToken(var_name))  # Put back the variable token
                        return parse_comparator()
            case _:
                return parse_declaration()

    def parse_declaration():
        match t.peek(None):
            case TypeToken(var_type):
                if var_type not in datatypes.keys():
                    raise TypeError(f"Invalid type: {var_type}")
                else :
                    next(t)
                    match t.peek(None):
                        case VariableToken(var_name):
                            if var_name in keywords:
                                raise SyntaxError(f"Invalid variable name: {var_name}")
                            else:
                                next(t)
                                match t.peek(None):
                                    case OperatorToken('='):
                                        next(t)
                                        value = parse_comparator()
                                        return Declaration(var_type, var_name, value)
                                    case _:
                                        raise SyntaxError("Expected '=' after variable name")
                        case _:
                            raise SyntaxError("Expected variable name")
            case _:
                return parse_comparator()
                                   
    def parse_comparator():
        ast = parse_add()
        while True:
            match t.peek(None):
                case OperatorToken(op):
                    if op in {"<", ">", "==", "!="}:
                        next(t)
                        ast = BinOp(op, ast, parse_sub())
                    else:
                        raise SyntaxError("Unexpected operator")
                case _:
                    return ast

    def parse_add():
        ast = parse_sub()
        while True:
            match t.peek(None):
                case OperatorToken('+'):
                    next(t)
                    ast = BinOp('+', ast, parse_sub())
                case _:
                    return ast
                
    def parse_sub():
        ast = parse_mul()
        while True:
            match t.peek(None):
                case OperatorToken('-'):
                    next(t)
                    ast = BinOp('-', ast, parse_mul())
                case _:
                    return ast


    def parse_mul():
        ast = parse_div()
        while True:
            match t.peek(None):
                case OperatorToken('*'):
                    next(t)
                    ast = BinOp('*', ast, parse_div())
                case _:
                    return ast

    def parse_div():
        ast = parse_exponent()
        while True:
            match t.peek(None):
                case OperatorToken('/'):
                    next(t)
                    divisor = parse_exponent()
                    ast = BinOp('/', ast, divisor)
                case _:
                    return ast


    def parse_exponent():
        ast = parse_atom()
        while True:
            match t.peek(None):
                case OperatorToken('^'):
                    next(t)
                    ast = BinOp('^', ast, parse_exponent())
                case _:
                    return ast

    def parse_atom():
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
                                        raise SyntaxError("Expected ')'")
                            case _:
                                raise SyntaxError("Expected ','")
                    case _:
                        raise SyntaxError("Expected '('")
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
                        raise SyntaxError("Expected ')'")
            case StringToken(v):
                next(t)
                return String(v)
            case _:
                raise SyntaxError("Unexpected token")

    return parse_condition()

# print(e(parse("2.5^2")))         #6.25
# print(e(parse("2+3^2")))         # 11
# print(e(parse("3 != 2")))        # 0
# print(e(parse("(2+3) > 4")))     # 1
# print(e(parse("6/3*2")))         # 4 (6 / 3 * 2)
# print(e(parse("6/3+2")))         # 4 (6 / 3 + 2)
# print(e(parse("2+6/3")))         # 4 (2 + 6 / 3)
# print(e(parse("2*3/4")))         # 1.5 (2 * 3 / 4)
# print(e(parse("2^3^2")))         # 512 (2^(3^2))
# print(e(parse("(2+3)*4/2")))     # 10((2+3) * 4 / 2)
# print(e(parse("2+3-4*5/2")))     # -5 (2 + 3 - 20 / 2)
# print(e(parse("2+3 > 4")))       # 1 (True: 2+3 > 4)
# print(e(parse("2+6/3 == 4")))    # 1 (True: 2 + 6/3 == 4)
# print(e(parse("2.5-3-4")))       #-4.5
# print(e(parse("2>3>6")))         #0
# print(parse("2 !< 3"))  
# print(e(parse("true + true"))) # 4
# print(e(parse("if 4>3 then int a = 4 else int a = 0"))) # 4
# print(parse("if 4>3 then int a = 4 else int a = 0"))
# print(e(parse("float y = 2.5"))) # 2.5
# print(e(parse("bool z = true"))) # True
# print(e(parse("if False then 10 else 20")))  # 20
# print(e(parse("if (4>2) then 1 else 0")))  # 1
# print(e(parse("~4+6/0")))           #division by zero 
print(e(parse("int x = 4")))

# compiler forces float to be like '1.0' is this right ? 
# print(e(parse("float x = x * 5"))) # rn this raises error but what should be the output
# print(e(parse("if (x-2)>0 then true else false")))  # 0
print(e(parse("x==10")))


print(e(parse(' concat("45", "3" )' )))
# concat not +
# repeat not *
