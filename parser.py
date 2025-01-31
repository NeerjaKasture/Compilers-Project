from dataclasses import dataclass
from collections.abc import Iterator
from more_itertools import peekable


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
class Paranthesis(AST):
    expr: AST


def e(tree: AST) -> float:
    match tree:
        case Paranthesis(expr):
            return e(expr)
        case Number(v):
            return float(v)
        case BinOp("+", l, r):
            return e(l) + e(r)
        case BinOp("*", l, r):
            return e(l) * e(r)
        case BinOp("-", l, r):
            return e(l) - e(r)
        case BinOp("/", l, r):
            return e(l) / e(r)
        case BinOp("^", l, r):
            return e(l) ** e(r)
        case BinOp("<", l, r):
            return float(e(l) < e(r))
        case BinOp("<=", l, r):
            return float(e(l) <= e(r))
        case BinOp(">", l, r):
            return float(e(l) > e(r))
        case BinOp(">=", l, r):
            return float(e(l) >= e(r))
        case BinOp("==", l, r):
            return float(e(l) == e(r))
        case BinOp("!=", l, r):
            return float(e(l) != e(r))
        case Cond(If, Then, Else):
            return e(Then) if e(If) else e(Else)

class Token:
    pass


@dataclass
class NumberToken(Token):
    v: str


@dataclass
class ParenthesisToken(Token):
    p: str

@dataclass
class KeywordToken(Token):
    value: str

@dataclass
class OperatorToken(Token):
    o: str


def lex(s: str) -> Iterator[Token]:
    i = 0
    while i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1

        if i >= len(s):
            return

        if s[i].isalpha():
            start = i
            while i < len(s) and s[i].isalpha() :
                i += 1
            word = s[start:i]
            if word in {'if', 'then', 'else'}:
                yield KeywordToken(word)
            else:
                raise SyntaxError(f"Unexpected identifier: {word}")

        elif s[i].isdigit() :
            t = s[i]
            i += 1
            has_decimal = False
            while i < len(s) and (s[i].isdigit() or (s[i] == '.' and not has_decimal)):
                if s[i] == '.':
                    has_decimal = True
                t += s[i]
                i += 1
            yield NumberToken(t)

        else:
            match s[i]:
                case '+' | '*' | '-' | '/' | '^' | '(' | ')' | '<' | '>' | '=' | '!'| '~':
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
                condition = parse_condition()  

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
                        raise SyntaxError("Expected 'else' after 'then' branch")

                else_branch = parse_condition() 
                return Cond(condition, then_branch, else_branch)

            case _:
                return parse_comparator() 


    def parse_comparator():
        ast = parse_sub()
        while True:
            match t.peek(None):
                case OperatorToken(op) if op in {"<", ">", "==", "!=", "<=", ">="}:
                    next(t)
                    ast = BinOp(op, ast, parse_sub())
                case _:
                    return ast

    def parse_sub():
        ast = parse_add()
        while True:
            match t.peek(None):
                case OperatorToken('-'):
                    next(t)
                    ast = BinOp('-', ast, parse_add())
                case _:
                    return ast

    def parse_add():
        ast = parse_mul()
        while True:
            match t.peek(None):
                case OperatorToken('+'):
                    next(t)
                    ast = BinOp('+', ast, parse_mul())
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
                    if isinstance(divisor, Number) and float(divisor.val) == 0:
                        raise ZeroDivisionError("Division by zero is not allowed.")
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
            case OperatorToken('~'):  # Check for the tilde operator
                next(t)
                return BinOp('*', Number('-1'), parse_atom())
            case NumberToken(v):
                next(t)
                return Number(v)
            case ParenthesisToken('('):
                next(t)
                expr = parse_condition()  
                match next(t, None):
                    case ParenthesisToken(')'):
                        return Paranthesis(expr)
                    case _:
                        raise SyntaxError("Expected ')'")
            case _:
                raise SyntaxError("Unexpected token")

    return parse_condition()

print(e(parse("2.5^2")))         #6.25
print(e(parse("2+3^2")))         # 11
print(e(parse("3 == 2")))        # 0
print(e(parse("(2+3) > 4")))     # 1
print(e(parse("6/3*2")))         # 4 (6 / 3 * 2)
print(e(parse("6/3+2")))         # 4 (6 / 3 + 2)
print(e(parse("2+6/3")))         # 4 (2 + 6 / 3)
print(e(parse("2*3/4")))         # 1.5 (2 * 3 / 4)
print(e(parse("2^3^2")))         # 512 (2^(3^2))
print(e(parse("(2+3)*4/2")))     # 10((2+3) * 4 / 2)
print(e(parse("2+3-4*5/2")))     # -5 (2 + 3 - 20 / 2)
print(e(parse("2+3 > 4")))       # 1 (True: 2+3 > 4)
print(e(parse("2+6/3 == 4")))    # 1 (True: 2 + 6/3 == 4)
print(e(parse("2.5-3-4")))       #-4
print(e(parse("2>3>6")))         #0
print(e(parse("if 2 < 3 then 4 else 5")))  # 4
print(e(parse("if 3 > 4 then 10 else 20")))  # 20
print(e(parse("if (if 2>3 then 0 else 1) then 1 else 0")))  # 1

print(e(parse("~4+6/0")))           #division by zero 


