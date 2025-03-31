from dataclasses import dataclass, field
from collections.abc import Iterator
from keywords import keywords, datatypes

@dataclass
class Token:
    pass

@dataclass
class NumberToken(Token):
    val: str

@dataclass
class ParenthesisToken(Token):
    val: str

@dataclass
class KeywordToken(Token):
    val: str

@dataclass
class OperatorToken(Token):
    val: str

@dataclass
class BooleanToken(Token):
    val: str

@dataclass
class StringToken(Token):
    val: str

@dataclass
class VariableToken(Token):
    val: str

@dataclass
class TypeToken(Token):
    val: str

@dataclass
class SymbolToken(Token):
    val: str



def lex(s: str) -> Iterator[Token]:
    i = 0
    while i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1

        if i >= len(s):
            return            

        if s[i].isalpha():
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == '_' or s[i] == '.'):
                i += 1
            word = s[start:i]
            if word in datatypes.keys():
                yield TypeToken(word)
            elif word in keywords:
                if word in ["nocap", "cap"]:
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
        
        elif s[i] == '#':
            while i < len(s) and s[i] != '\n':
                i += 1
            continue


        else:
            match s[i]:
                case '+' | '*' | '-' | '/' | '^' | '(' | ')' | '<' | '>' | '=' | '!' | '~' | '{' | '}' | ';' | ',' | '[' | ']' | '->'|'%':
                    if i + 1 < len(s):
                        two_char_op = s[i:i + 2]
                        if two_char_op in {"<=", ">=", "==", "!=","~~"}:  # Explicitly handle <=, >=
                            yield OperatorToken(two_char_op)
                            i += 2
                            continue
                    if s[i] in "}(){[]$":
                        yield ParenthesisToken(s[i])
                    elif s[i] == '-' and i + 1 < len(s) and s[i + 1] == '>':
                        yield SymbolToken('->')
                        i += 2
                    elif s[i] in '+ * - / ^ ~><=':
                        yield OperatorToken(s[i])
                    else:
                        yield SymbolToken(s[i])
                    i += 1
                # Handle bitwise operators separately
                case '&' | '|':
                    yield OperatorToken(s[i])
                    i += 1
                case _:
                    raise ValueError(f"Unexpected character: {s[i]}")

